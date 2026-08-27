# Authority precedence

When two documents disagree, the higher entry wins.

1. A direct written Captain ruling in the current conversation.
2. `authority/01-DECISION-REGISTER.md` and `authority/05-SUPERSESSIONS.md`.
3. `project.yaml` and `authority/03-OWNERSHIP-MATRIX.csv`.
4. `contracts/` interface documents.
5. `architecture/` documents.
6. Everything else in this repository.
7. Documents in other SpectraSynq repositories.
8. `archive/` material — evidence only, never authority.

## Rules

- A later document that merely mentions a topic does not supersede an earlier explicit ruling
  on that topic. Superseding requires an entry in `05-SUPERSESSIONS.md`.
- A contract that cannot be located is not frozen, whatever an earlier note called it.
- Vendor datasheets and manufacturer documentation outrank internal prose on component facts.
- Measurements outrank estimates. Estimates outrank recollection.
