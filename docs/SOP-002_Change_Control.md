# SOP-002: Change Control Management

**Document ID:** SOP-002  
**Version:** 1.0  
**Effective Date:** 2026-04-06  
**Classification:** GMP-Controlled Document  

---

## 1. Purpose

This Standard Operating Procedure (SOP) establishes the process for evaluating, approving, implementing, and documenting changes to GxP-compliant systems within the OncoSML platform.

## 2. Scope

This SOP applies to all changes affecting:
- Software applications used in clinical trials
- Infrastructure supporting GxP systems
- Validated computerized systems
- Documentation affecting product quality or patient safety

## 3. Definitions

| Term | Definition |
|------|------------|
| Change Control | Formal process for managing changes to validated systems |
| Change Request (CR) | Formal proposal for a change |
| Change Control Board (CCB) | Group responsible for reviewing and approving changes |
| Validated State | Condition where system performs as intended consistently |
| Re-validation | Testing to confirm system remains in validated state after change |

## 4. Responsibilities

### 4.1 Change Requestor
- Submit complete change request
- Provide justification and supporting documentation
- Participate in impact assessment
- Implement approved changes

### 4.2 Change Control Board (CCB)
**Members:**
- QA Manager (Chair)
- Development Lead
- Validation Lead
- Clinical Affairs Representative
- IT/Security Representative

**Responsibilities:**
- Review change requests
- Assess impact on validated state
- Approve or reject changes
- Ensure proper documentation

### 4.3 Quality Assurance
- Oversee change control process
- Ensure compliance with regulations
- Approve changes affecting product quality
- Audit change control activities

### 4.4 System Owner
- Accountable for system performance
- Approve changes within authority
- Ensure resources for implementation
- Maintain system documentation

## 5. Change Classification

### 5.1 Classification Criteria

| Category | Patient Safety Impact | Product Quality Impact | Regulatory Impact | System Complexity |
|----------|----------------------|------------------------|-------------------|-------------------|
| Minor | None | None | None | Low |
| Moderate | Low | Low | Low | Medium |
| Major | Medium | Medium | Medium | High |
| Critical | High | High | High | Very High |

### 5.2 Category Definitions

#### Minor Changes
- Documentation corrections (typos, formatting)
- Non-functional UI changes
- Performance optimizations with no functional impact
- Security patches (non-critical)

**Approval:** QA Manager  
**Re-validation:** None  
**Examples:**
- Correcting spelling in user manual
- Changing button color
- Updating help text

#### Moderate Changes
- Bug fixes for non-critical issues
- Minor feature enhancements
- Configuration changes
- Database index additions

**Approval:** CCB (expedited)  
**Re-validation:** Targeted testing  
**Examples:**
- Fixing calculation rounding display
- Adding new report format
- Updating reference data

#### Major Changes
- New functionality
- Architecture modifications
- Database schema changes
- Integration with new systems

**Approval:** Full CCB + QA  
**Re-validation:** Partial (affected areas)  
**Examples:**
- Adding new analysis module
- Changing data storage structure
- Modifying user authentication

#### Critical Changes
- Changes affecting patient dosing
- Modifications to validated algorithms
- Changes required by regulatory authority
- Emergency security fixes

**Approval:** Full CCB + Regulatory + Senior Management  
**Re-validation:** Full  
**Examples:**
- Modifying neoantigen prediction algorithm
- Changing dose calculation logic
- Emergency patch for data breach

## 6. Change Control Process

### 6.1 Change Request Submission

**Required Information:**
1. **Change Description**
   - Clear, detailed description of proposed change
   - Current state vs. proposed state
   - Technical approach

2. **Justification**
   - Reason for change
   - Expected benefits
   - Risks of not implementing

3. **Impact Assessment (Preliminary)**
   - Affected systems/modules
   - Potential impact on patients
   - Regulatory implications
   - Resource requirements

4. **Proposed Timeline**
   - Development duration
   - Testing duration
   - Target implementation date

### 6.2 Change Request Logging

All change requests must be logged in the Change Control System with:
- Unique CR number (format: CR-YYYY-NNNN)
- Date submitted
- Requestor information
- Initial classification
- Status tracking

### 6.3 Impact Assessment

**Detailed Assessment Required:**

1. **Patient Safety Impact**
   - Could this change affect patient treatment?
   - Could this change affect clinical decisions?
   - Risk assessment using ICH Q9 principles

2. **Product Quality Impact**
   - Could this change affect data integrity?
   - Could this change affect system reliability?
   - Impact on validated state

3. **Regulatory Impact**
   - Does this require regulatory notification?
   - Does this affect submission documents?
   - Impact on compliance status

4. **Technical Impact**
   - Affected components and interfaces
   - Data migration requirements
   - Backward compatibility
   - Performance implications

5. **Resource Impact**
   - Development effort (hours)
   - Testing effort (hours)
   - Validation effort (hours)
   - Training requirements
   - Infrastructure changes

### 6.4 CCB Review and Approval

**Review Process:**
1. CCB meeting scheduled (within 5 business days for non-urgent)
2. Requestor presents change request
3. CCB discusses impact and risks
4. CCB votes on approval

**Decision Options:**
- **Approve** - Change may proceed as proposed
- **Approve with Conditions** - Change approved with specific requirements
- **Reject** - Change not approved, requestor may resubmit with modifications
- **Defer** - Decision postponed, additional information required

**Approval Criteria:**
- Impact assessment complete and satisfactory
- Risks identified and mitigated
- Resources allocated
- Timeline realistic
- Validation strategy appropriate

### 6.5 Implementation

**After Approval:**

1. **Development**
   - Develop in isolated environment
   - Follow SOP-001 Software Development
   - Document all changes
   - Unit test thoroughly

2. **Testing**
   - Execute test plan per validation strategy
   - Document all test results
   - Address any failures
   - Obtain QA sign-off on testing

3. **Documentation Updates**
   - Update affected documents
   - Revise procedures if needed
   - Update training materials
   - Revise system documentation

### 6.6 Verification and QA Review

**QA Verification:**
- Confirm change implemented as approved
- Verify testing complete and passed
- Review documentation updates
- Confirm training completed
- Verify no adverse impact on validated state

### 6.7 Deployment

**Pre-Deployment:**
- Backup current system
- Prepare rollback plan
- Notify stakeholders
- Schedule deployment window

**Deployment:**
- Follow deployment procedure
- Monitor for issues
- Verify functionality
- Document deployment

**Post-Deployment:**
- Monitor system performance
- Address any issues promptly
- Update configuration records
- Conduct post-implementation review

### 6.8 Change Closure

**Closure Requirements:**
- All implementation activities complete
- Testing passed and documented
- Documentation updated
- Training completed
- QA approval obtained
- Lessons learned documented

## 7. Emergency Changes

### 7.1 Definition
Emergency changes are those required immediately to:
- Address critical security vulnerabilities
- Restore system functionality after failure
- Prevent patient harm
- Comply with regulatory directive

### 7.2 Emergency Process

1. **Verbal Approval**
   - Obtain verbal approval from CCB Chair and QA
   - Document verbal approval

2. **Implementation**
   - Implement change immediately
   - Document all actions taken
   - Test to extent possible

3. **Retroactive Documentation**
   - Submit formal change request within 24 hours
   - Complete impact assessment
   - Obtain formal CCB approval within 5 business days

4. **Post-Emergency Review**
   - Conduct root cause analysis
   - Identify preventive measures
   - Update procedures if needed

## 8. Periodic Review

### 8.1 Change Control Metrics

| Metric | Target | Frequency |
|--------|--------|-----------|
| Average CR processing time | < 30 days | Monthly |
| Emergency changes | < 5% of total | Quarterly |
| CRs requiring rework | < 10% | Quarterly |
| On-time implementation | > 90% | Monthly |

### 8.2 Trend Analysis
- Analyze change patterns
- Identify recurring issues
- Assess process effectiveness
- Recommend improvements

## 9. Training

### 9.1 Required Training
- This SOP
- Change control system usage
- Impact assessment methodology
- Role-specific responsibilities

### 9.2 Training Frequency
- Initial: Before participating in change control
- Refresher: Every 2 years
- Update: When SOP is revised

## 10. References

1. FDA 21 CFR Part 11 - Electronic Records and Signatures
2. FDA 21 CFR Part 820 - Quality System Regulation
3. ICH Q9 - Quality Risk Management
4. ICH Q10 - Pharmaceutical Quality System
5. GAMP 5 - A Risk-Based Approach to Compliant GxP Computerized Systems

## 11. Appendices

### Appendix A: Change Request Form Template
### Appendix B: Impact Assessment Checklist
### Appendix C: Change Control Log Template

## 12. Revision History

| Version | Date | Description | Author | Approved By |
|---------|------|-------------|--------|-------------|
| 1.0 | 2026-04-06 | Initial release | System | QA Manager |

---

**Prepared By:** ___________________ Date: _________

**Reviewed By (QA):** ___________________ Date: _________

**Approved By:** ___________________ Date: _________

---

*This document is controlled under the Quality Management System. Unauthorized copying or distribution is prohibited.*