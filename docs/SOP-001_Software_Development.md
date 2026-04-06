# SOP-001: Software Development and Change Control

**Document ID:** SOP-001  
**Version:** 1.0  
**Effective Date:** 2026-04-06  
**Classification:** GMP-Controlled Document  

---

## 1. Purpose

This Standard Operating Procedure (SOP) defines the requirements and processes for developing, testing, and maintaining GxP-compliant software systems within the OncoSML platform.

## 2. Scope

This SOP applies to all software development activities for systems that:
- Support clinical trial operations
- Process patient data (PHI)
- Generate regulatory submissions
- Impact product quality or patient safety

## 3. Responsibilities

### 3.1 Development Team
- Write code following established standards
- Perform unit testing
- Document code changes
- Participate in code reviews

### 3.2 Quality Assurance
- Review and approve development procedures
- Audit development activities
- Approve releases for production

### 3.3 Validation Team
- Develop validation protocols
- Execute qualification testing
- Document validation results

### 3.4 Change Control Board
- Review and approve significant changes
- Assess impact on validated state
- Authorize deployment to production

## 4. Development Process

### 4.1 Requirements Definition
1. Document functional requirements in User Requirements Specification (URS)
2. Define technical requirements in Functional Specification (FS)
3. Obtain stakeholder approval before development begins

### 4.2 Design Phase
1. Create detailed design documentation
2. Review design for GxP compliance
3. Identify critical components requiring validation

### 4.3 Development Standards

#### Coding Standards
- Follow PEP 8 style guide for Python code
- Include comprehensive docstrings
- Use type hints for function signatures
- Implement error handling and logging

#### Code Comments
```python
# Bad: Redundant comment
x = x + 1  # Increment x by 1

# Good: Explains why
x = x + 1  # Adjust for zero-based indexing in external API
```

#### Function Documentation
```python
def calculate_dosage(patient_weight: float, drug_concentration: float) -> float:
    """
    Calculate drug dosage based on patient weight.
    
    Args:
        patient_weight: Patient weight in kg
        drug_concentration: Drug concentration in mg/mL
        
    Returns:
        Calculated dosage in mL
        
    Raises:
        ValueError: If weight or concentration is invalid
        
    GxP Impact: HIGH - Direct patient dosing calculation
    """
```

### 4.4 Version Control

#### Branch Strategy
- `main` - Production-ready code (protected)
- `develop` - Integration branch for features
- `feature/*` - Feature development branches
- `release/*` - Release preparation branches
- `hotfix/*` - Emergency production fixes

#### Commit Standards
```
[TYPE] Brief description

Detailed description if needed

GxP-Impact: HIGH/MEDIUM/LOW
JIRA: PROJ-123
```

Types:
- `FEAT` - New feature
- `FIX` - Bug fix
- `DOCS` - Documentation changes
- `STYLE` - Code formatting
- `REFACTOR` - Code restructuring
- `TEST` - Test additions/changes
- `CHORE` - Maintenance tasks

### 4.5 Code Review Process

#### Review Requirements
- All GxP-impactful code must be reviewed
- At least one reviewer must be familiar with GxP requirements
- Security-sensitive code requires security team review

#### Review Checklist
- [ ] Code follows established standards
- [ ] Adequate test coverage exists
- [ ] Error handling is implemented
- [ ] Logging is appropriate
- [ ] Security considerations addressed
- [ ] Documentation is complete
- [ ] GxP impact assessed

### 4.6 Testing Requirements

#### Unit Testing
- Minimum 80% code coverage for GxP components
- 100% coverage for critical calculations
- Tests must be automated and repeatable

#### Integration Testing
- Test interfaces between components
- Verify data flow and transformations
- Test error conditions and recovery

#### User Acceptance Testing
- End users verify functionality meets requirements
- Test in environment that mirrors production
- Document test results and obtain sign-off

## 5. Change Control

### 5.1 Change Classification

| Category | Description | Approval Required | Re-validation |
|----------|-------------|-------------------|---------------|
| Minor | Documentation, non-functional changes | QA Manager | None |
| Moderate | Bug fixes, minor enhancements | Change Control Board | Targeted |
| Major | New features, architecture changes | Change Control Board + QA | Full/Patial |
| Critical | Changes affecting patient safety | Full Board + Regulatory | Full |

### 5.2 Change Request Process

1. **Submit Change Request**
   - Document proposed change
   - Describe rationale and expected benefits
   - Identify potential risks

2. **Impact Assessment**
   - Evaluate effect on validated state
   - Assess patient safety impact
   - Determine testing requirements
   - Estimate resources and timeline

3. **Approval**
   - Obtain required approvals based on category
   - Document approval in change control system

4. **Implementation**
   - Develop change in isolated environment
   - Perform required testing
   - Update documentation

5. **Verification**
   - QA verifies change meets requirements
   - Confirm no adverse impact on existing functionality

6. **Deployment**
   - Deploy to production following release procedures
   - Update system documentation
   - Train affected users if necessary

7. **Closure**
   - Document completion
   - Archive change control record

## 6. Release Management

### 6.1 Release Preparation

1. **Code Freeze**
   - No new features accepted
   - Only critical bug fixes allowed

2. **Release Candidate Build**
   - Build in controlled environment
   - Generate release notes
   - Create deployment package

3. **Final Testing**
   - Execute regression test suite
   - Performance testing
   - Security scanning

### 6.2 Release Approval

**Required Signatures:**
- Development Lead: Confirms code complete
- QA Manager: Confirms testing complete
- Validation Lead: Confirms validation complete
- Change Control Board: Authorizes production deployment

### 6.3 Deployment

1. **Pre-Deployment**
   - Backup current production system
   - Prepare rollback plan
   - Notify stakeholders

2. **Deployment Execution**
   - Follow documented deployment procedure
   - Monitor for errors
   - Verify system functionality

3. **Post-Deployment**
   - Verify system performance
   - Monitor for issues
   - Update documentation
   - Conduct post-implementation review

## 7. Documentation Requirements

### 7.1 Development Documentation
- Requirements specifications
- Design documents
- Test plans and results
- Code review records
- Change control records

### 7.2 User Documentation
- User manuals
- Standard operating procedures
- Training materials
- Quick reference guides

### 7.3 System Documentation
- Installation guides
- Configuration documentation
- Architecture diagrams
- Data flow diagrams

## 8. Training

### 8.1 Required Training
- GxP fundamentals
- This SOP
- Role-specific procedures
- System-specific training

### 8.2 Training Records
- Document all training activities
- Maintain training logs
- Assess competency
- Schedule refresher training (annual minimum)

## 9. Quality Metrics

### 9.1 Development Metrics
- Code review completion rate
- Test coverage percentage
- Defect density
- Time to resolve critical issues

### 9.2 Quality Gates
- All critical bugs resolved
- Test coverage meets minimum requirements
- Documentation complete and approved
- Security scan passed
- Performance benchmarks met

## 10. References

1. FDA 21 CFR Part 11 - Electronic Records and Signatures
2. ICH Q9 - Quality Risk Management
3. GAMP 5 - A Risk-Based Approach to Compliant GxP Computerized Systems
4. IEC 62304 - Medical Device Software Lifecycle Processes

## 11. Revision History

| Version | Date | Description | Author | Approved By |
|---------|------|-------------|--------|-------------|
| 1.0 | 2026-04-06 | Initial release | System | QA Manager |

---

**Prepared By:** ___________________ Date: _________

**Reviewed By (QA):** ___________________ Date: _________

**Approved By:** ___________________ Date: _________

---

*This document is controlled under the Quality Management System. Unauthorized copying or distribution is prohibited.*