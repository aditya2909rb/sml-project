"""One-shot script to clean up the corrupted safety_validator.py."""
import pathlib

src = pathlib.Path('sml/safety_validator.py')
lines = src.read_text(encoding='utf-8').splitlines(keepends=True)
print(f'Input: {len(lines)} lines')

CLEAN_MRNA_METHOD = '''\
    def validate_mrna_sequence(self, sequence: str, construct_info: Dict[str, Any]) -> List[ValidationResult]:
        """Validate mRNA sequence safety and quality."""
        results = []

        sequence_upper = sequence.upper().strip()

        if len(sequence_upper) < self.validation_rules['mrna_sequence']['min_length']:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"mRNA sequence too short: {len(sequence_upper)} < {self.validation_rules[\'mrna_sequence\'][\'min_length\']}",
                {\'length\': len(sequence_upper), \'min_length\': self.validation_rules[\'mrna_sequence\'][\'min_length\']}
            ))

        if len(sequence_upper) > self.validation_rules['mrna_sequence']['max_length']:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"mRNA sequence too long: {len(sequence_upper)} > {self.validation_rules[\'mrna_sequence\'][\'max_length\']}",
                {\'length\': len(sequence_upper), \'max_length\': self.validation_rules[\'mrna_sequence\'][\'max_length\']}
            ))

        # Check base composition
        allowed_bases = self.validation_rules[\'mrna_sequence\'][\'allowed_bases\']
        invalid_bases = set(sequence_upper) - allowed_bases
        if invalid_bases:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"Invalid RNA bases found: {invalid_bases}",
                {\'invalid_bases\': list(invalid_bases), \'allowed_bases\': list(allowed_bases)}
            ))

        if not sequence_upper:
            return results

        # Check GC content
        gc_count = sequence_upper.count(\'G\') + sequence_upper.count(\'C\')
        gc_content = gc_count / len(sequence_upper)

        if gc_content < self.validation_rules[\'mrna_sequence\'][\'min_gc_content\']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"mRNA GC content too low: {gc_content:.2%} < {self.validation_rules[\'mrna_sequence\'][\'min_gc_content\']:.2%}",
                {\'gc_content\': gc_content, \'min_gc_content\': self.validation_rules[\'mrna_sequence\'][\'min_gc_content\']}
            ))

        if gc_content > self.validation_rules[\'mrna_sequence\'][\'max_gc_content\']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"mRNA GC content too high: {gc_content:.2%} > {self.validation_rules[\'mrna_sequence\'][\'max_gc_content\']:.2%}",
                {\'gc_content\': gc_content, \'max_gc_content\': self.validation_rules[\'mrna_sequence\'][\'max_gc_content\']}
            ))

        # Check for repetitive motifs
        repeated_motifs = self._count_repeated_motifs(sequence_upper)
        if repeated_motifs > self.validation_rules[\'mrna_sequence\'][\'max_repeated_motifs\']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"Too many repeated motifs: {repeated_motifs} > {self.validation_rules[\'mrna_sequence\'][\'max_repeated_motifs\']}",
                {\'repeated_motifs\': repeated_motifs, \'max_repeated_motifs\': self.validation_rules[\'mrna_sequence\'][\'max_repeated_motifs\']}
            ))

        # Check self-complementarity
        self_comp = self._calculate_self_complementarity(sequence_upper)
        if self_comp > self.validation_rules[\'mrna_sequence\'][\'max_self_complementarity\']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"High self-complementarity: {self_comp:.2%} > {self.validation_rules[\'mrna_sequence\'][\'max_self_complementarity\']:.2%}",
                {\'self_complementarity\': self_comp, \'max_self_complementarity\': self.validation_rules[\'mrna_sequence\'][\'max_self_complementarity\']}
            ))

        # Check for cryptic splice sites
        if self._check_splice_sites(sequence_upper):
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                "mRNA contains potential cryptic splice sites",
                {\'sequence\': sequence_upper[:100] + "..." if len(sequence_upper) > 100 else sequence_upper}
            ))

        # Check for internal ribosome entry sites (IRES)
        if self._check_ires(sequence_upper):
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                "mRNA contains potential IRES elements",
                {\'sequence\': sequence_upper[:100] + "..." if len(sequence_upper) > 100 else sequence_upper}
            ))

        # --- Stricter biological gates ---

        # CpG density: high obs/expected ratio triggers TLR9-mediated innate immune activation.
        cpg_count = sequence_upper.count(\'CG\')
        c_freq = sequence_upper.count(\'C\') / len(sequence_upper)
        g_freq = sequence_upper.count(\'G\') / len(sequence_upper)
        expected_cpg = c_freq * g_freq * len(sequence_upper)
        if expected_cpg > 0:
            cpg_oe_ratio = cpg_count / expected_cpg
            if cpg_oe_ratio > 0.6:
                results.append(ValidationResult(
                    SafetyLevel.WARNING,
                    f"High CpG dinucleotide density (obs/exp {cpg_oe_ratio:.2f} > 0.60); "
                    "may trigger innate immune activation via TLR9",
                    {\'cpg_count\': cpg_count, \'cpg_oe_ratio\': round(cpg_oe_ratio, 4)}
                ))

        # Internal stop codon detection across all three reading frames.
        stop_codons = {\'UAA\', \'UAG\', \'UGA\'}
        premature_stops = []
        for frame in range(3):
            for pos in range(frame, len(sequence_upper) - 5, 3):
                codon = sequence_upper[pos : pos + 3]
                if codon in stop_codons and pos + 3 < len(sequence_upper) - 3:
                    premature_stops.append((pos, codon))
        if premature_stops:
            first_pos, first_codon = premature_stops[0]
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"Premature stop codon {first_codon} at position {first_pos} "
                f"({len(premature_stops)} occurrence(s) across all frames)",
                {\'premature_stop_count\': len(premature_stops),
                 \'first_occurrence\': {\'position\': first_pos, \'codon\': first_codon}}
            ))

        return results

'''

new_lines = []
i = 0
while i < len(lines):
    line_no = i + 1  # 1-based

    # Replace entire bad validate_mrna_sequence block (lines 325-449)
    if line_no == 325:
        new_lines.append(CLEAN_MRNA_METHOD)
        while i + 1 <= 449:
            i += 1
        continue

    # Fix line 460: corrupted def inside validate_vaccine_construct
    if line_no == 460:
        new_lines.append(
            "                f\"Vaccine construct too long: {total_length} > "
            "{self.validation_rules['vaccine_construct']['max_total_length']}\",\n"
        )
        i += 1
        continue

    # Fix line 494: stray def (should be closing `))`)
    if line_no == 494:
        new_lines.append('            ))\n')
        i += 1
        continue

    # Fix line 509: μ -> ug
    if line_no == 509:
        new_lines.append(lines[i].replace('\u03bcg', 'ug'))
        i += 1
        continue

    # Remove dead code block inside _calculate_hydrophobicity (lines 580-619)
    if 580 <= line_no <= 619:
        i += 1
        continue

    new_lines.append(lines[i])
    i += 1

src.write_text(''.join(new_lines), encoding='utf-8')
print(f'Output: {len(new_lines)} lines')
print('Done.')
