# v1.0.0
- Initial version

# v1.0.2
- Added strict "Anti-Nesting" filter: daemons can no longer be substrings of each other, preventing shorter sequences from being automatically completed inside longer ones.
- Reworked sequence intersection mechanism: daemons are now forced to overlap only by their edges, demanding strategic route planning and high buffer utilization from the player.
- Optimized unique byte validation within each daemon sequence to eliminate overly simple or repetitive combinations.
- Guaranteed 100% level solvability across all difficulties (Lamer, IRC Member, Hacker) through multi-pass cyclic verification of generated path slices.
