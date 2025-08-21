````markdown
# Chatbot Monitoring Flow

## Overview

This document describes the monitoring pipeline for our chatbot system, including PII detection, latency tracking, and error handling.

## Monitoring Architecture

```mermaid
flowchart TD
    A[User Request] --> B[Chatbot API]
    B --> C[Generate Response]
    C --> D[Monitoring Service]

    subgraph "Monitoring Pipeline"
        D --> E[PII Detection]
        D --> F[Latency Measurement]
        D --> G[Error Checking]
        E --> H[Log Results]
        F --> H
        G --> H
        H --> I[Alert System]
    end

    I --> J[Safe Response]
    I --> K[Blocked Response<br>if critical PII]

    J --> L[Return to User]
    K --> M[Return Error Message]

    H --> N[Feedback System]
    N --> O[Continuous Improvement]
```
````
