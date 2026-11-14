# Security notes: committed Postgres data

Copyright (c) 2026 Galion Labs. This file is covered by the repository licence.

This note records an audit of Postgres data files that were committed to this repository, and a plan for removing them from history. It does not rewrite history, force-push, delete branches, rotate passwords, or change any running service. Nothing in this plan should be carried out without Slavik's written go-ahead.

Secret values and personal data are omitted on purpose. The audit classified kinds of data and counted them. It did not copy verifiers, salts, or row contents into this file.

## What was committed

| Item | Value |
| --- | --- |
| Path | `v1/galion/data/postgres/pgdata/` |
| Tracked files | 968 |
| Working tree size | 28 MB allocated, about 38.0 MB apparent |
| Unique git blobs | 313 blobs, 24,906,048 bytes uncompressed |
| Introducing commit | `c5976ba692793741a6f9d32b32a84787e897e61c` |
| Commit date | 2025-11-12 16:23:17 +0100 |
| Commit subject | NexusLang v2 Production Release - Clean Initial Commit |
| Later modifications | none |

The three database directories under `base/` are byte-identical, so git stores one copy of those files. The single WAL segment is a 16 MB sparse file (`pg_wal/000000010000000000000001`).

That commit is the root of `main`. The same blobs are therefore on:

- `main`
- `cursor/galion-coin-alpha-9a4b` (one commit ahead of `main`)
- `tidy/galion-hygiene-20261114` (draft PR #2 removes the files from the tree; the blobs stay in history)

`clean-nexuslang` is a separate history. It does not contain this root commit, and it does not contain `pgdata/`.

The same root commit also added 25,194 files under `v1/galion/services/galion-alpha/frontend/node_modules/` (about 236 MB on disk, 20,121 unique blobs, about 145 MB uncompressed). Those files were not modified by any later commit. This audit did not read them for secrets. They are listed because any history rewrite that drops the database directory should drop them in the same pass. Draft PR #2 already untracks them from the tree.

## What the data is

The directory is a PostgreSQL 15 cluster (`PG_VERSION` is `15`, catalog version `202209061`, `pg_control` version `1300`). It is the data directory of a running official Docker Postgres image, not a SQL fixture file.

Evidence of that layout, with no secret values:

- `postmaster.opts` names `/usr/local/bin/postgres`.
- `postmaster.pid` names data directory `/var/lib/postgresql/data/pgdata`, port 5432, and a start time of 2025-11-10 20:49:04 UTC.
- The control file state is in production, checkpointed at 2025-11-10 20:54:10 UTC. Cluster system identifier: `7571201263934205987`.
- `postgresql.conf` sets `listen_addresses = '*'`.
- `pg_hba.conf` has the stock local `trust` lines plus one Docker-entrypoint line: `host all all all scram-sha-256`.
- `postgresql.auto.conf` has the stock header only. No `ALTER SYSTEM` settings.

Catalog contents, read from the heap files:

- Databases: `template0` (oid 4), `template1` (oid 1), and `postgres` (oid 5). No other database. All three have `datfrozenxid` 717, which is the level of a cluster that has barely been written to.
- Schemas in database `postgres`: `pg_toast`, `pg_catalog`, `public`, `information_schema`. The `public` schema has zero relations.
- Roles: 13. Twelve are the stock `pg_*` predefined roles and have no password. One role can log in. It is the bootstrap superuser (oid 10), the role name is `nexuscore`, and it has a SCRAM-SHA-256 verifier at the default iteration count. No password expiry is set. No other role has a password.
- The same verifier is stored a second time in `pg_wal/000000010000000000000001`.
- A byte scan of the whole `pgdata/` tree found no email addresses, no `postgres://` or other URLs, no cloud access-key prefixes, no PEM private keys, and no API-key prefixes.
- `pg_stat_tmp/pgss_query_texts.stat` holds one parameterized catalog lookup (`SELECT $1 FROM pg_database WHERE datname = $2`). It contains no bound literals.

## How to read that

This is not a production dump of application data, and it is not a test fixture of seed rows. There are no user tables, no user rows, and no personal data in the cluster. It is a live data directory from a container that had reached production state, with a real superuser password verifier and otherwise empty catalogs.

The verifier is a credential. The repository is public, so the verifier should be treated as exposed. Anyone who still uses that password for the `nexuscore` role, on any host, should rotate it. Rotation is independent of a history rewrite. This note does not rotate it, and it does not record the verifier.

Local `trust` authentication is also present. A copy of this data directory started on a machine would allow any local operating-system user to connect as the superuser, in addition to remote SCRAM logins.

## Sibling data in the same commit

Draft PR #2 untracks the 968 Postgres files and the 25,194 `node_modules` files. It does not untrack the rest of `v1/galion/data/`, which is still in the tree on `tidy/galion-hygiene-20261114`:

| Path | Files | Size | Kind |
| --- | --- | --- | --- |
| `v1/galion/data/redis/` | 3 | 176 bytes | Redis AOF manifest plus a tiny base RDB. The incremental AOF is empty. No emails, URLs, or key-like strings. |
| `v1/galion/data/prometheus/` | 15 | about 10.3 MB | Prometheus TSDB. Two blocks plus head and WAL, 660 series, samples from 2025-11-10 20:49 UTC through 2025-11-11 00:00 UTC. A byte scan found no emails, URLs, SCRAM verifiers, cloud keys, or PEM keys. |

The root `.gitignore` already lists `v1/galion/data/`, which does not remove tracked files. Untracking these 18 files is a small follow-up. The history plan below drops the whole `v1/galion/data/` tree.

## What this change does

This pull request only hardens `.gitignore` and adds this note.

`.gitignore` now ignores `node_modules/`, `pgdata/`, WAL and stats directories, postmaster pid files, `data/postgres/`, `data/redis/`, `data/prometheus/`, Redis AOF directories, and `*.rdb`, including copies outside `v1/galion/data/`. Ignore rules do not remove files that are already tracked. Until draft PR #2 is merged, or until history is rewritten, `pgdata/` and `node_modules/` stay in the tree on `main`.

This pull request does not edit `LICENSE`. The licence question on draft PR #2 is still open.

## History rewrite plan

Do not run this plan from this branch. Do not force-push. Do not delete branches. Each publishing step needs Slavik's written go-ahead.

1. Rotate the `nexuscore` password on every live server that was initialized from this data directory or from the same password. Do that even if the rewrite is declined. Do not paste the verifier into a ticket, a commit, or a chat.
2. Confirm the public repo still has no forks, and list clones that would need a fresh fetch after a rewrite. On 2026-11-14 GitHub reported zero forks.
3. On a fresh mirror clone, filter history with a tool such as `git filter-repo`. The paths to drop are `v1/galion/data/` and every `node_modules` directory. Example, for a mirror that is not this working tree:

   ```
   git filter-repo --invert-paths \
     --path v1/galion/data/ \
     --path-glob '**/node_modules/**'
   ```

4. Expect every commit SHA on `main` and on `cursor/galion-coin-alpha-9a4b` to change, because the blobs were added in the root commit. Leave `clean-nexuslang` out of this rewrite. It does not contain these blobs.
5. Review the rewritten clone locally. `git rev-list --objects --all` should show no path under `v1/galion/data/` and no path under `node_modules/`. Confirm the rest of the tree is intact.
6. Only after written approval, force-push the rewritten `main` and the rewritten coin branch. Coordinate anyone who has a clone. Draft PR #2 will not apply after the SHAs change. Recreate its licence and ignore-rule edits on the new history, or drop that pull request if the filter already removed the files.
7. Ask GitHub to purge the old objects from the public repository. A rewrite plus a force-push does not by itself erase objects GitHub has already served, and it does not erase clones that already exist.
8. Turn on secret scanning and push protection so a data directory or a password verifier cannot be pushed again. The `.gitignore` rules in this pull request are the local half of that control.
9. Do not delete `tidy/galion-hygiene-20261114`, `clean-nexuslang`, or `cursor/galion-coin-alpha-9a4b` as part of the filter. Deleting a branch is a separate decision.

## Decisions for Slavik

1. Rotate the exposed `nexuscore` superuser password on any live database that still uses it.
2. Approve or decline the history rewrite above. Declining leaves the verifier in the public history after PR #2 untracks the files.
3. Approve or decline untracking the 15 Prometheus files and 3 Redis files that PR #2 left in the tree.
4. Approve or decline the licence edit already sitting on draft PR #2. This note does not change it.
5. After a rewrite, whether to ask GitHub to purge cached objects, and whether to enable secret scanning and push protection.
