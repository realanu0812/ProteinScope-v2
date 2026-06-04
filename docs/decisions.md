# Architecture Decision Records

This file tracks important technical decisions made during the project.

## Decision 1: Use Monorepo

We will use a monorepo structure with separate apps for frontend and backend.

Reason:
- Easier development
- Easier deployment coordination
- Better for a full-stack AI project

## Decision 2: Separate Evidence and Community Sources

Scientific papers and Reddit/community experiences will be stored and retrieved separately.

Reason:
- Scientific evidence is verified
- Reddit data is anecdotal
- The final answer should never mix anecdotal reports with scientific claims
