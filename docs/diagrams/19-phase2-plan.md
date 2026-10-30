# 19. Phase II work plan (Gantt)

**Notation:** Project plan  
**Project:** Auditable AI Agents

## What it shows

The planned work for next semester. Dates are illustrative: shift the start date to match your semester calendar.

## Diagram

```mermaid
gantt
  title Phase II plan (illustrative dates)
  dateFormat YYYY-MM-DD
  axisFormat %b
  tickInterval 1month
  section Evaluation
  Gas against batch size           :a1, 2027-01-04, 28d
  Overhead per agent step          :a2, after a1, 21d
  Verification scaling to 100000   :a3, after a2, 21d
  section Application
  Dashboard of verified entries    :b1, after a2, 35d
  Signed entries (optional)        :b2, after b1, 14d
  section Writing
  Verify all references            :c1, 2027-01-04, 14d
  Evaluation write-up and thesis   :c2, after a3, 42d
  Viva preparation                 :c3, after c2, 14d
```

![Phase II work plan (Gantt)](images/19-phase2-plan.png)

## Where it comes from

`docs/methodology/evaluation-plan.md` (experiments 2 to 4) and Table 6.1 of the Phase I report. This plan is not yet carried out.
