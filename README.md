# supasara

A bilingual field guide to supply chain English, with searchable vocabulary, practical articles, and complete PDF and EPUB editions.

在真实工作场景中学习供应链英语：双语术语、实用文章，以及完整 PDF 与 EPUB 电子书。

## Features

- 177 Markdown articles organized into seven categories.
- 469 vocabulary entries, with Chinese/English search and category filters.
- Article contents navigation, bilingual tables, related topics, and previous/next reading links.
- Responsive layouts for desktop and mobile readers.
- Complete downloadable PDF (507 pages) and reflowable EPUB editions, including all articles and a vocabulary index.
- Context notes preserve different meanings of abbreviations such as ABC and JIT; uncertain terminology is explicitly marked.

## Development

Requires Node.js 20.19 or newer and Yarn 4.18.1 (pinned via Corepack).

```sh
corepack yarn install --immutable
corepack yarn run dev
```

Open http://localhost:3000. Run `corepack enable` once to make the `yarn` command available, or use `corepack yarn` in place of `yarn`. Commit `yarn.lock` and use `yarn install --immutable` in CI. The project uses the node-modules linker.

### Windows: Yarn 1 version mismatch

If `yarn run dev` reports that global Yarn 1.22.22 does not match `yarn@4.18.1`, use `corepack yarn run dev`. This invokes the pinned version directly, without requiring a global Yarn replacement. Verify it from the project directory with `corepack yarn --version`; the expected result is `4.18.1`.

To enable the shorter `yarn` command permanently, run `corepack enable yarn`. When Node.js is installed under `C:\Program Files\nodejs`, this may require a PowerShell terminal opened **as Administrator**. After enabling, reopen your normal terminal, return to the project directory, and run `yarn --version` followed by `yarn run dev`. If the version still reports 1.x, run `where.exe yarn` to identify an older launcher earlier in PATH; continue using `corepack yarn` until that command-path conflict is resolved. Keep the project's `packageManager` field and Yarn lockfile.

See the [official Yarn Corepack guide](https://yarnpkg.com/corepack).

### Windows: garbled Chinese paths in MODULE_NOT_FOUND

If an error replaces `小红书` with garbled characters while locating Next.js, the command launcher has changed the path's encoding. The project scripts invoke the installed JavaScript entry points directly through Node using relative paths, avoiding Windows package executable shims. Run `corepack yarn run dev` as usual. This also applies to the build, TypeScript, and browser-test scripts. No folder rename or global code-page change is required.

The application uses Next.js App Router, React, TypeScript, Tailwind CSS, and `react-markdown` with `remark-gfm`. Markdown tables, lists, headings, and emphasis are rendered as semantic HTML. Raw HTML in articles is not enabled.

## Shared content

```text
content/                 Canonical Markdown articles and collection/vocabulary metadata
scripts/prepare.mjs      Validate content and prepare website/search data
scripts/build_books.py   Generate both complete books from prepared content
app/                     Website routes and styles
components/              Markdown and search components
lib/                     Content access and search logic
public/downloads/        Complete books and their version/size/hash manifest
tests/                   Content/search checks and browser scenarios
```

The repository contains a standalone copy of the previously prepared shared content. Use `content/` as the publication source going forward; the earlier `Output/05_Shared_Content` folder remains a historical snapshot. Changes there are not automatically synchronized.

Edit the Markdown and metadata together, preserving stable article IDs and vocabulary references. Then run:

```sh
yarn prepare:content
yarn test
```

Preparation validates article IDs, categories, required sections, vocabulary mappings, and related links. It generates `data/content.json` and `public/data/search.json`; these generated folders are ignored by Git. Both development and production builds prepare content automatically. Search runs in the reader's browser without a database or external search service.

## Author profile

Author: 雨叔. 小红书账号：雨叔 北美仓储管理. The About page and both books share `content/author.json`. The supplied account card is stored unchanged at `public/images/yushu-rednote.png` and embedded in the EPUB for offline access. Regenerate both books after changing the profile or image.

## Complete books

Ready-to-download editions are in `public/downloads/`. They contain the entire collection, not sample articles. Website deployment serves these existing files and does not require Python.

To regenerate after editing content:

```sh
python -m pip install -r requirements-books.txt
yarn prepare:content
yarn books
```

The PDF builder needs Chinese TrueType fonts. On Windows it defaults to Microsoft YaHei from the system Fonts folder. On another system, set `BOOK_FONT` and `BOOK_FONT_BOLD` to compatible font file paths. Fonts are not distributed in this repository. The EPUB uses the reader's fonts.

The book builder verifies EPUB XML and internal links, checks that all 177 article titles occur in the PDF, and updates `public/downloads/manifest.json`. Review representative rendered PDF pages and an EPUB reader after editorial or layout changes. Regenerate and commit both books and their manifest whenever publication content changes; a website build alone does not refresh books.

## Verification

```sh
yarn prepare:content
yarn test
yarn build
yarn check
yarn playwright install chromium webkit
yarn test:browser
```

The browser suite covers desktop/mobile reading, Markdown tables, search, ambiguous terms, and book download endpoints. It serves the production `out/` directory on port 3177, so run `yarn build` first. It does not reuse another running application.

Verified on 2026-10-27: Yarn immutable installation, the production static build, TypeScript checks, all five content/search/download tests, and all ten browser checks passed. Browser checks cover Chromium desktop and WebKit mobile against the built static export. Desktop and mobile screenshots were visually reviewed. Both full books were generated; EPUB structure and internal links passed checks; representative PDF pages were visually inspected.

## Local production preview

Run `yarn build`, then `yarn preview`, and open http://127.0.0.1:3177. If Yarn shims are not enabled, use `corepack yarn preview`. This loopback-only server previews the static export; Vercel serves the files directly in production.

On Windows, OneDrive can mark generated folders read-only and cause `EPERM` during directory cleanup. The development and build commands now run `scripts/prepare-cache.mjs`, which clears only the read-only directory attribute within `.next` and `out` on Windows; it does not delete files or traverse directory links. Development uses Next.js Webpack mode because OneDrive can reapply attributes while Turbopack replaces its generated chunk directory. Stop an existing development server with Ctrl+C before restarting `corepack yarn run dev`. Production builds retain the default bundler.

## Vercel deployment

Import the `hugoplus/supasara` GitHub repository into Vercel. Use the repository root as the project root and the Next.js framework preset. Install with `yarn install --immutable` and build with `yarn build`. Corepack selects the version pinned in `package.json`; include `yarn.lock` and `.yarnrc.yml` in the repository.

`next.config.ts` enables static export, producing `out/`. The site requires no API server or database. Use Vercel's static-export handling (or `out/` as the output directory if configuring it manually). Preview the deployment and run the browser checks before publishing. Do not use `next start` to serve the static export.

## License

See [LICENSE](LICENSE) for the repository's existing Apache License 2.0.
