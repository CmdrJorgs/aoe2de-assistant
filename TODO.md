# AoE2 Coach AI — UI/UX & Tactical Engine TODOs

## Tactical Metrics & Data Sources
- [ ] **Unified Confidence Score Metric**: Verify whether the backend inference engine should return a top-level `unified_confidence_score` (0.00-1.00) combining ONNX classifier certainty, counter-matrix heuristic score, and LLM explanation verification. Currently using `tactical_stance.confidence` / `military_action_plan.confidence` (defaulting to 78%).
- [ ] **Action Timing Urgency Calibration**: Confirm whether attack timing windows (e.g. "Next 3 minutes") should sync with a live in-game match timer or match clock countdown via WebSockets/polling.
- [ ] **Eco Health Macro Grade**: Macro grade is currently mapped from `economic_rebalance.macro_health_grade` (defaulting to 'C' when pending initial recommendation). Confirm if grade threshold algorithm (A-F) should consider floating stockpile penalties.

## Navigation & Secondary Views
- [ ] **History View**: Implement match snapshot history and tactical timeline replay under the "History" navigation tab.
- [ ] **Tactics & Combat Duel Simulator**: The new slimmed-down War Room interface focuses on the 3-step rapid input and tactical metrics sidebar. Decide if the Combat Duel Simulator widget should be embedded under the "Tactics" navigation view or as a slide-over drawer.
- [ ] **Codex & Tech Tree Explorer**: Integrate full civilizational tech trees and unit stats database under the "Codex" view using the local `CivTechTrees/*.json` datasets.
- [ ] **Support / About**: Add user documentation and bug report links under the "Support" view.

## Asset Integration & Visuals
- [ ] **Civ-Specific Unique Tech Icons**: Add unique technology icons into civ selection details or advice tooltips.
- [ ] **Sound Effects / Audio Feedback**: Optional audio cue (medieval horn or horn sound) when Recalculate completes or when an urgency threat alert is triggered.
