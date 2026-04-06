from pathlib import Path
import json

# Find the most recent vaccine design file
model_store = Path('model_store')
json_files = sorted(model_store.glob('vaccine_design_*.json'))
if json_files:
    latest = json_files[-1]
    print(f'✓ Latest design file: {latest.name}')
    
    with open(latest, encoding='utf-8') as f:
        data = json.load(f)
    
    # Save full design as JSON
    design_file = Path('outputs/VALIDATION_DESIGN.json')
    design_file.parent.mkdir(exist_ok=True)
    with open(design_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f'✓ Full design saved to: outputs/VALIDATION_DESIGN.json')
    
    # Save report as markdown
    report_file = Path('outputs/VALIDATION_REPORT.md')
    report_file.write_text(data['report_markdown'], encoding='utf-8')
    print(f'✓ Report saved to: outputs/VALIDATION_REPORT.md')
    
    # Print summary
    print(f'\n--- DESIGN SUMMARY ---')
    print(f"Sample: {data.get('sample_id', 'N/A')}")
    print(f"Timestamp: {data.get('timestamp', 'N/A')}")
    print(f"Immunogenicity profiles: {len(data.get('immunogenicity', {}).get('profiles', []))}")
    print(f"HLA predictions: {data.get('hla_binding', {}).get('total_predictions', 0)}")
    print(f"mRNA sequence length: {data.get('mrna_construct', {}).get('sequence_length_nt', 0)} nt")
    clin = data.get('clinical_readiness', {})
    print(f"Clinical recommendation: {clin.get('recommendation', 'N/A')}")
    print(f"Trial eligibility: {clin.get('trial_eligibility', 'N/A')}")
