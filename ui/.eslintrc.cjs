module.exports = {
  ignorePatterns: ['dist'],
  overrides: [
    {
      files: ['**/*.{js,jsx,ts,tsx}'],
      env: { browser: true, es2021: true },
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: { jsx: true },
      },
      extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended'],
      parser: '@typescript-eslint/parser',
      plugins: ['@typescript-eslint', 'react-hooks'],
      rules: {
        'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }],
      },
    },
  ],
}
