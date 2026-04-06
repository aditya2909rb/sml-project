"""Fix validate_complete_pipeline and generate_safety_report in safety_validator.py."""
import pathlib

src = pathlib.Path('sml/safety_validator.py')
lines = src.read_text(encoding='utf-8').splitlines(keepends=True)
print(f'Input: {len(lines)} lines')

NEW_METHODS = """\
    def validate_complete_pipeline(
        self,
        dna_sequence: str,
        neoantigens: list,
        mrna_construct: dict,
        neoantigen_metadata=None,
    ):
        \"\"\"Validate the complete vaccine design pipeline.

        Args:
            neoantigen_metadata: Optional list of per-neoantigen dicts with
                ``binding_affinity_nm`` and/or ``immunogenicity_score`` keys
                so stricter per-peptide biological gates can be applied.
        \"\"\"
        validation_results = {
            'dna_validation': self.validate_dna_sequence(dna_sequence, "sample_001"),
            'neoantigen_validation': [],
            'mrna_validation': self.validate_mrna_sequence(
                mrna_construct.get('sequence', ''), mrna_construct
            ),
            'construct_validation': self.validate_vaccine_construct(mrna_construct),
        }
        for i, neoantigen in enumerate(neoantigens):
            meta = {'index': i}
            if neoantigen_metadata and i < len(neoantigen_metadata):
                meta.update(neoantigen_metadata[i])
            validation_results['neoantigen_validation'].extend(
                self.validate_neoantigen(neoantigen, meta)
            )
        return validation_results

    def generate_safety_report(self, validation_results):
        \"\"\"Generate a JSON-serializable safety report from pipeline validation results.\"\"\"
        total_checks = 0
        critical_issues = 0
        warnings = 0
        passed_checks = 0
        serializable_details = {}

        for category, results in validation_results.items():
            serializable_details[category] = []
            for result in results:
                total_checks += 1
                if result.level == SafetyLevel.CRITICAL:
                    critical_issues += 1
                elif result.level == SafetyLevel.WARNING:
                    warnings += 1
                else:
                    passed_checks += 1
                serializable_details[category].append({
                    'level': result.level.value,
                    'message': result.message,
                    'details': result.details,
                })

        if critical_issues > 0:
            overall_status = 'CRITICAL'
        elif warnings > 5:
            overall_status = 'WARNING'
        else:
            overall_status = 'PASS'

        recommendations = []
        if critical_issues > 0:
            recommendations.append("Address all critical safety issues before proceeding")
        if warnings > 0:
            recommendations.append("Review and address safety warnings")
        if total_checks == 0:
            recommendations.append("No validation checks performed")

        return {
            'summary': {
                'total_checks': total_checks,
                'critical_issues': critical_issues,
                'warnings': warnings,
                'passed_checks': passed_checks,
                'overall_status': overall_status,
            },
            'detailed_results': serializable_details,
            'recommendations': recommendations,
        }

"""

# Keep lines 1-689 (0-indexed 0-688)
# Replace lines 690-845 (0-indexed 689-844) with NEW_METHODS
# Keep lines 847+ (0-indexed 846+)
new_lines = lines[:689] + [NEW_METHODS] + lines[846:]

src.write_text(''.join(new_lines), encoding='utf-8')
print(f'Output: {len(new_lines)} lines')
print('Done.')
