import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from ssi.config import load_config, set_seed

def main():
    config = load_config()
    set_seed(config["seed"])
    
    steps = [
        ("S0: Project scaffold", None),
        ("S1: Ingestion", "from ssi.ingest import main as s1; s1()"),
        ("S2: Photo processing", "from ssi.photos import main as s2; s2()"),
        ("S3: QC", "from ssi.qc import process_qc as s3; s3()"),
        ("S4: Feature extraction", "from ssi.features import process_features as s4; s4()"),
        ("S5: Targets", "from ssi.targets import build_datasets as s5; s5()"),
        ("S6: Sampling", "from ssi.sampling import main as s6; s6()"),
        ("S7: Modeling Boys", "from ssi.modeling_boys import run_modeling as s7; s7()"),
        ("S8: Modeling Girls", "from ssi.modeling_girls import run_modeling as s8; s8()"),
        ("S9: Girls Descriptives", "from ssi.descriptives_girls import produce_girls_descriptives as s9; s9()"),
        ("S10: Tape Agreement", "from ssi.tape_agreement import process_tape_agreement as s10; s10()"),
        ("S11: Experiments", "from ssi.experiments import process_experiments as s11; s11()"),
        ("S12a: Figures", "from ssi.figures import main as s12a; s12a()"),
        ("S12b: Verification", "from ssi.verify import main as s12b; s12b()"),
        ("S14a: Report Skeleton", "from ssi.report import main as s14a; s14a()"),
        ("S14b: Check Report", "from ssi.check_report import check_report as s14b; s14b('outputs/report/report_skeleton.md')")
    ]
    
    for step_name, step_cmd in steps:
        print(f"Running {step_name}...")
        if step_cmd:
            exec(step_cmd)

if __name__ == "__main__":
    main()

