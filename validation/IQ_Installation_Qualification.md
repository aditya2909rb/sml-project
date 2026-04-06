# Installation Qualification (IQ) Protocol

**Document ID:** SML-IQ-001  
**Version:** 1.0  
**Effective Date:** 2026-04-06  
**System:** OncoSML mRNA Vaccine System  
**Classification:** GMP-Controlled Document  

---

## 1. Introduction

### 1.1 Purpose
This Installation Qualification (IQ) protocol verifies that the OncoSML system is installed correctly in the production environment with all required components, configurations, and infrastructure.

### 1.2 Scope
This protocol covers:
- Hardware verification
- Software installation verification
- Network configuration verification
- Security configuration verification
- Database installation verification

---

## 2. Prerequisites

| # | Prerequisite | Status | Verified By | Date |
|---|--------------|--------|-------------|------|
| 1 | Validation Master Plan approved | ☐ | | |
| 2 | User Requirements Specification approved | ☐ | | |
| 3 | Test environment ready | ☐ | | |
| 4 | Installation procedures documented | ☐ | | |
| 5 | Personnel trained on procedures | ☐ | | |

---

## 3. System Description

### 3.1 Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer                           │
│                   (NGINX/HAProxy)                          │
├─────────────────────────────────────────────────────────────┤
│          Application Servers (Docker Containers)            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Web API   │ │  Workers    │ │  Scheduler  │           │
│  │   :8000     │ │   :8001     │ │   :8002     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│              Data Services                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  PostgreSQL │ │    Redis    │ │   MinIO     │           │
│  │  (Primary)  │ │  (Cache)    │ │  (Storage)  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Components

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Runtime environment |
| PostgreSQL | 15+ | Primary database |
| Redis | 7+ | Session/cache store |
| Docker | 24+ | Containerization |
| NGINX | 1.24+ | Reverse proxy |

---

## 4. Installation Verification Tests

### 4.1 Hardware Verification

| Test ID | Test Description | Acceptance Criteria | Pass/Fail | Verified By | Date |
|---------|------------------|---------------------|-----------|-------------|------|
| IQ-HW-01 | Server CPU verification | Minimum 8 cores, 2.5 GHz+ | ☐ | | |
| IQ-HW-02 | Memory verification | Minimum 32 GB RAM | ☐ | | |
| IQ-HW-03 | Storage verification | Minimum 500 GB SSD | ☐ | | |
| IQ-HW-04 | Network connectivity | 1 Gbps network interface | ☐ | | |
| IQ-HW-05 | Redundancy verification | UPS and backup power | ☐ | | |

### 4.2 Operating System Verification

| Test ID | Test Description | Acceptance Criteria | Pass/Fail | Verified By | Date |
|---------|------------------|---------------------|-----------|-------------|------|
| IQ-OS-01 | OS version verification | Ubuntu 22.04 LTS or equivalent | ☐ | | |
| IQ-OS-02 | Security updates | All security patches applied | ☐ | | |
| IQ-OS-03 | Time synchronization | NTP configured and synced | ☐ | | |
| IQ-OS-04 | File system | ext4 or xfs with proper mount options | ☐ | | |
| IQ-OS-05 | User accounts | Service accounts created with proper permissions | ☐ | | |

### 4.3 Software Installation Verification

| Test ID | Test Description | Acceptance Criteria | Pass/Fail | Verified By | Date |
|---------|------------------|---------------------|-----------|-------------|------|
| IQ-SW-01 | Python installation | Python 3.11+ installed and accessible | ☐ | | |
| IQ-SW-02 | Docker installation | Docker 24+ installed and running | ☐ | | |
| IQ-SW-03 | PostgreSQL installation | PostgreSQL 15+ installed and running | ☐ | | |
| IQ-SW-04 | Redis installation | Redis 7+ installed and running | ☐ | | |
| IQ-SW-05 | NGINX installation | NGINX 1.24+ installed and running | ☐ | | |
| IQ-SW-06 | Dependencies installed | All Python packages installed per requirements.txt | ☐ | | |

### 4.4 Network Configuration Verification

| Test ID | Test Description | Acceptance Criteria | Pass/Fail | Verified By | Date |
|---------|------------------|---------------------|-----------|-------------|------|
| IQ-NET-01 | Firewall configuration | Only required ports open (80, 443, 5432, 6379) | ☐ | | |
| IQ-NET-02 | SSL/TLS configuration | TLS 1.3 configured with valid certificates | ☐ | | |
| IQ-NET-03 | DNS configuration | Hostname resolves correctly | ☐ | | |
| IQ-NET-04 | Load balancer | Health checks configured and passing | ☐ | | |
| IQ-NET-05 | Network isolation | Database not accessible from public internet | ☐ | | |

### 4.5 Database Installation Verification

| Test ID | Test Description | Acceptance Criteria | Pass/Fail | Verified By | Date |
|---------|------------------|---------------------|-----------|-------------|------|
| IQ-DB-01 | Database creation | OncoSML database created | ☐ | | |
| IQ-DB-02 | User permissions | Application user has correct permissions | ☐ | | |
| IQ-DB-03 | Encryption at rest | TDE or equivalent encryption enabled | ☐ | | |
| IQ-DB-04 | Backup configuration | Automated backup configured | ☐ | | |
| IQ-DB-05 | Connection test | Application can connect to database | ☐ | | |

### 4.6 Security Configuration Verification

| Test ID | Test Description | Acceptance Criteria | Pass/Fail | Verified By | Date |
|---------|------------------|---------------------|-----------|-------------|------|
| IQ-SEC-01 | Access control | RBAC implemented and configured | ☐ | | |
| IQ-SEC-02 | Audit logging | Audit trail module configured | ☐ | | |
| IQ-SEC-03 | Encryption | All data encrypted in transit (TLS 1.3) | ☐ | | |
| IQ-SEC-04 | Password policy | Password complexity requirements enforced | ☐ | | |
| IQ-SEC-05 | Session management | Session timeout configured (30 minutes) | ☐ | | |

---

## 5. Documentation Verification

| Document ID | Document Name | Version | Available | Verified |
|-------------|---------------|---------|-----------|----------|
| SML-URS-001 | User Requirements Specification | 1.0 | ☐ | ☐ |
| SML-DS-001 | Design Specification | 1.0 | ☐ | ☐ |
| SML-VMP-001 | Validation Master Plan | 1.0 | ☐ | ☐ |
| SOP-001 | Software Development SOP | 1.0 | ☐ | ☐ |
| SOP-002 | Change Control SOP | 1.0 | ☐ | ☐ |
| | Architecture Diagrams | | ☐ | ☐ |
| | Network Diagrams | | ☐ | ☐ |
| | Installation Procedures | | ☐ | ☐ |

---

## 6. Deviations

| Deviation # | Description | Impact Assessment | Resolution | Status |
|-------------|-------------|-------------------|------------|--------|
| | | | | |

---

## 7. Summary and Approval

### 7.1 IQ Summary

| Category | Total Tests | Passed | Failed | N/A |
|----------|-------------|--------|--------|-----|
| Hardware | 5 | | | |
| Operating System | 5 | | | |
| Software | 6 | | | |
| Network | 5 | | | |
| Database | 5 | | | |
| Security | 5 | | | |
| **Total** | **31** | | | |

### 7.2 IQ Conclusion

☐ **PASS** - All acceptance criteria met, system ready for OQ  
☐ **FAIL** - Acceptance criteria not met, corrective action required

### 7.3 Technical Groundwork Status (Software Layer)

- Technical IQ baseline execution completed for software and security prerequisites.
- Evidence: `validation/evidence/IQ-TECH-BASELINE_TS-008_20260406_164711.json`
- Evidence register: `validation/IQ_EVIDENCE_LOG.md`
- Infrastructure-specific production checks (hardware/network/DB hardening in target environment) remain pending formal execution.

### 7.4 Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Prepared By | | | |
| Reviewed By (QA) | | | |
| Approved By | | | |

---

*This document is controlled under the Quality Management System.*