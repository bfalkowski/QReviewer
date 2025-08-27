# Learning Results Directory

This directory contains AI learning results from different repositories.

## Structure

```
learning_results/
├── qreviewer/                    # QReviewer repository learning results
│   ├── combined_learning_results.json
│   ├── module_qrev_results.json
│   └── module_tests_results.json
├── example_repos/                # Other repositories you've trained on
│   ├── react/                    # React repository results
│   ├── vscode/                   # VS Code repository results
│   └── tensorflow/               # TensorFlow repository results
└── README.md                     # This file
```

## Adding New Repository Results

When you train on a new repository, create a new folder:

```bash
# Train on a new repository
qrev learn https://github.com/owner/repo \
  --module src \
  --output-dir learning_results/new_repo_name

# The system will create:
# learning_results/new_repo_name/
# ├── combined_learning_results.json
# ├── module_src_results.json
# └── other_module_results.json
```

## File Naming Convention

- **Repository folders**: Use descriptive names (e.g., `react`, `vscode`, `company_monorepo`)
- **Combined results**: `combined_learning_results.json`
- **Module results**: `module_{module_name}_results.json`

## Best Practices

1. **Organize by repository**: Keep each repository's results in its own folder
2. **Use descriptive names**: Make folder names clear and searchable
3. **Archive old results**: Move outdated results to an `archive/` subfolder
4. **Document changes**: Add notes about what changed between training runs
5. **Version control**: Consider adding `.gitignore` for large result files

## Example Usage

```bash
# List all trained repositories
ls learning_results/

# View results from a specific repository
cat learning_results/react/combined_learning_results.json | jq '.summary'

# Compare results between repositories
diff learning_results/react/combined_learning_results.json \
      learning_results/vscode/combined_learning_results.json
```
