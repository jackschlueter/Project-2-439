# Lab 20 — Pre-Run Prediction

**Analyst:** Jack Schlueter  
**Date:** November 22, 2026  
**Decision:** PILOT  
**Test:** Equity Expected Return Sensitivity

## 1. Load-Bearing Input

I will reduce the expected annual return on global equities from **8.00% to 7.25%**, a decrease of 0.75 percentage points. All other assumptions, including volatility, correlations, costs, the 3% eligible reserve requirement, and the proposed 10% loss limit, will remain unchanged.

I selected this input because equities represent 55% of the current recommended portfolio and contribute significantly to achieving Meridian's 6.5% return hurdle.

## 2. Predicted Results

The current portfolio consists of 0% Treasury bills, 20% 10-year Treasuries, 25% investment-grade bonds, and 55% global equities. It produces an expected return of 6.51%, volatility of 9.44%, and a 95% one-year loss measure of 9.02%.

If the portfolio weights remain unchanged, reducing the equity return assumption by 0.75 percentage points should decrease the expected portfolio return by approximately 0.41 percentage points:

0.55 × 0.75 = 0.4125 percentage points.

This would reduce the expected portfolio return from approximately 6.51% to 6.10%, below the required 6.5% hurdle.

I expect the optimizer to increase equity exposure to compensate for the lower expected return. However, this would also increase portfolio volatility and the modeled one-year loss. Because the portfolio is already close to the proposed 10% loss limit, I predict that the optimizer will struggle to find an allocation satisfying both the return and risk requirements.

## 3. Expected Effect on the Decision

**My prediction is that the mandate screen will change from PASS to FAIL and trigger the process's STOP condition**, meaning no portfolio on the 5% allocation grid will satisfy the return, reserve, and proposed loss constraints simultaneously.

I expect my overall recommendation to remain **PILOT**, rather than changing to ADOPT or REJECT.

A failed stress test would demonstrate that the process correctly identifies when the foundation's objectives cannot be met under its assumptions. However, it would also reinforce my concern that the current investment strategy is too sensitive to relatively small changes in expected returns.

## 4. What Would Change My Call?

If the model finds a portfolio that meets the return hurdle, maintains sufficient eligible reserves, and stays below the proposed loss limit after the equity return reduction, I would have greater confidence in the process's robustness.

If no qualifying portfolio exists, I would maintain the PILOT recommendation and require additional sensitivity testing and more defensible market estimates before considering adoption.

**This prediction is recorded before running the revised scenario.**
