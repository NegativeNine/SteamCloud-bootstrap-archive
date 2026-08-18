# Contributing

The JavaScript sample’s public surface is `src/index.js`. Forbidden field names live in `schemas/forbidden-fields.json`. Contract, authority and roadmap changes require matching documentation, schema fixtures and tests. Do not add credentials, generic upstream proxy fields, user-selected trust roots or hidden fallbacks. A production claim requires evidence, not only source or unit tests.

Validate with `npm run check` and `npm test`.
