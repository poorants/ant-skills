# Code Conventions

This is a **thin starting point** seeded by the bootstrap. Your stack was
auto-detected but there is no curated dedicated seed yet, so this holds only
universal rules. The accurate way to fill it in is to **extract** the real rules
from this repo's code with the `code-convention` skill.

## How to fill this in

```
/code-convention        # extract conventions from existing code -> update this doc
```

Extraction captures this project's actual naming, structure, error handling, and
test patterns as rules. Stack-specific rules are more trustworthy when pulled
from the code than guessed from a template.

## Universal baseline (temporary, pre-extraction)

The minimum that applies regardless of stack. Once extracted rules exist, they
take precedence.

1. **Naming consistency**: do not mix case conventions
   (camelCase/snake_case/PascalCase) within one codebase. Follow the dominant
   style already present in the code.
2. **Explicit error handling**: never swallow errors. When caught, handle them or
   rethrow with added context.
3. **Security basics**: never leave secrets (tokens, keys, passwords) in code,
   logs, or commits in plaintext. Use environment variables / a secret manager.
4. **Testability**: separate side effects from pure logic to keep test seams.
5. **Comments explain "why"**: capture why, not what. Do not duplicate in
   comments what the code already explains.

## Management

Add, edit, or check rules with the `code-convention` skill
(`/code-convention add`, `/code-convention check`, `/code-convention evolve`).
