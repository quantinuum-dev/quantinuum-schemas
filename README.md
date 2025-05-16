# Quantinuum schemas

Public models that define API boundaries used by Quantinuum.  Intended to be
used across teams and projects ie. shared. Backwards compatibility and semantic
versioning are particularly important in this repo!  The "Check Conventional
Commits format" workflow will make sure your PRs follow a [standard
format](https://www.conventionalcommits.org/en/v1.0.0/). For
backwards-incompatible changes, please use the conventional `!` or `BREAKING
CHANGE:`.

## Dependencies

We try to keep the dependencies minimal. However we do need `pydantic` for
validation.

# Making a release

See notes above about conventional commits and versioning.

Once all your code changes are merged onto the `main` branch using conventional
commits, follow these steps to publish.

## Update the CHANGELOG

- Update `CHANGELOG.md`: this is automated.

  Use `devenv` and the `commitizen`
  [tool](https://commitizen-tools.github.io/commitizen/):
  ```
  git fetch --tags origin  # make sure your local tags are same as in github
  cz bump --files-only  # --files-only prevents the tool making a git tag
  ```
  This will use the [commit history](https://www.conventionalcommits.org/) and
  modify `CHANGELOG.md` to include a heading with the new version number and the
  date. The tool automatically decides whether to increment the patch version,
  minor version or major version.

  If none of the commits since the last version tag would generate a CHANGELOG
  entry, then you will see `NO_COMMITS_TO_BUMP`. In this situation,

  ```shell
  >$ # only if you see NO_COMMITS_TO_BUMP... add one to the patch number
  >$ cz bump --files-only x.y.z+1  # !! substitute correct version
  >$ vi CHANGELOG.md  # edit to explain that there are no changes
  ```

- If you like, you can manually edit `CHANGELOG.md` at this point. Consider
  moving important entries under these headings, or writing under them (see
  [Keep A Changelog](https://keepachangelog.com/en/1.1.0/#how)):
  - Deprecated
  - Removed
  - Security
- Create a release branch `git checkout -b release/vx.y.z`
- `git add` the modifications, then `git commit` and `git push` them.
- Create a PR (title: `docs: Update CHANGELOG for vx.y.z`)
- Ask a colleague to review the changes (should be just `CHANGELOG.md` and
  `pyproject.toml`)
- Squash merge the PR into `main`

## Trigger the release workflow

- Go to github.com and on this repo's home page, click "Create a new release"
- Using the version in the format `v1.2.34`, click "Choose a tag" and create a
  new tag
- Click "Generate release notes"
- Release title = `v1.2.34`. In the "Describe this release" box, copy and paste
  the new text that was added to CHANGELOG.md in the commit you are releasing.
- Click "Publish release".
- The "Create release" workflow should run automatically.
- Check that the new release is on
  https://pypi.org/project/quantinuum-schemas/#history
