from ssi.gate import run_gate

def run_modeling():
    gate_status, gate_reason = run_gate("GIRLS")
    if gate_status == "NOT_FIT":
        print(f"Stopping model evaluation for GIRLS. Gate status: {gate_status} ({gate_reason})")
        return

if __name__ == "__main__":
    run_modeling()

