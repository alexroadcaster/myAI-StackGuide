"""Wire cardinality regression; no model calls, COUNT/MATCH or state writes."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cardinality_producer',
    ROOT/'evals/plugin-v1/run_final_host_calibration_cardinality.py')
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)


class HostOrderCardinality(unittest.TestCase):
    def test_observed_short_order_is_rejected_for_99_pool(self):
        short = {'decision_order':list(range(1,99))}
        # The old wire schema admits the real failure shape (98 unique IDs).
        Draft202012Validator(producer.shared.order_schema()).validate(short)
        bound = Draft202012Validator(producer.bound_order_schema(99))
        with self.assertRaises(ValidationError):
            bound.validate(short)
        with self.assertRaises(ValidationError):
            bound.validate({'decision_order':list(range(1,101))})
        bound.validate({'decision_order':list(range(1,100))})
        with self.assertRaises(ValidationError):
            bound.validate({'decision_order':[str(n) for n in range(1,100)]})

    def test_every_pool_count_fits_schema_reserve_without_prompt_change(self):
        original = copy.deepcopy(producer.shared.ORDER_SCHEMA)
        maximum = original['properties']['decision_order']['maxItems']
        for count in range(1,maximum+1):
            schema = producer.bound_order_schema(count)
            self.assertLessEqual(len(producer.canonical(schema)),producer.schema_reserve_bytes())
            expected = copy.deepcopy(original)
            expected['properties']['decision_order'].update(minItems=count,maxItems=count)
            self.assertEqual(schema,expected)
        self.assertEqual(producer.shared.ORDER_SCHEMA,original)
        preview={'candidates':[{'github_repository_id':1}], 'context':{'goal':'synthetic'}}
        self.assertEqual(producer.shared.order_prompt(preview),
            producer.shared.INSTRUCTION+producer.canonical(preview).decode()+producer.shared.SUFFIX)
        self.assertEqual(producer.schema_reserve_delta(),max(0,
            producer.schema_reserve_bytes()-len(producer.canonical(original))))
        for invalid in (0,maximum+1,True,1.0):
            with self.assertRaises(ValueError): producer.bound_order_schema(invalid)

    def test_all_four_actual_prepare_payloads_preserve_empty_observations(self):
        previous=json.loads((producer.original.OUTPUT/'cases.json').read_bytes())
        observed=[]
        class StopBeforeNative(Exception): pass
        def prepare_spy(decision,payload,wrapper_bytes):
            observed.append(payload)
            raise StopBeforeNative()
        with patch.object(producer.shared,'native_prepare',side_effect=prepare_spy):
            for row in producer.four_cases():
                with self.assertRaises(StopBeforeNative):
                    producer.capture_case(row,{'wrapper_reservations':{row['case_id']:0}}, {})
        expected=[dict(brief=next(p for p in previous if p['case_id']==r['case_id'])['brief'],
            interpretation=next(p for p in previous if p['case_id']==r['case_id'])['interpretation'],
            public_observations=[]) for r in producer.four_cases()]
        self.assertEqual(observed,expected)
        tree=ast.parse(Path(producer.original.__file__).read_text(encoding='utf-8'))
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and
            isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and
            n.func.value.id=='runtime' and n.func.attr=='run']
        self.assertEqual(len(calls),1)
        self.assertEqual(len(calls[0].args),2)
        self.assertFalse(calls[0].keywords)

    def test_cli_consumes_actual_per_case_schema_and_identical_prompt_once(self):
        preview={'candidates':[{'github_repository_id':n} for n in range(1,100)]}
        def cli_spy(command,**kwargs):
            schema_path=Path(command[command.index('--output-schema')+1])
            self.assertEqual(json.loads(schema_path.read_bytes()),producer.bound_order_schema(99))
            self.assertEqual(kwargs['input'],producer.shared.order_prompt(preview).encode())
            response=Path(command[command.index('--output-last-message')+1])
            response.write_text(json.dumps({'decision_order':list(range(1,100))}),encoding='utf-8')
            kwargs['stdout'].write(b'{"type":"turn.completed"}\n')
            self.assertEqual(kwargs['timeout'],240)
            self.assertNotIn('--model',command)
            return SimpleNamespace(returncode=0)
        with tempfile.TemporaryDirectory(prefix='cp04-cardinality-test-',dir=ROOT/'work') as directory:
            output=Path(directory)
            with patch.object(producer.shutil,'which',return_value='mock-codex'),\
                patch.object(producer.subprocess,'run',side_effect=cli_spy) as process:
                order,trace=producer.cardinality_host_order('synthetic',preview,output=output)
            self.assertEqual(process.call_count,1)
            self.assertEqual(order,list(range(1,100)))
            schema_bytes=(output/'synthetic/host-order.schema.json').read_bytes()
            self.assertEqual(trace['output_schema_utf8_bytes'],len(schema_bytes))
            self.assertEqual(trace['pool_count'],99)
            self.assertEqual(trace['controlled_prompt_and_schema_bytes'],
                len(producer.shared.order_prompt(preview).encode())+len(schema_bytes))
            self.assertEqual(trace['automatic_retries'],0)


if __name__=='__main__':
    unittest.main()
