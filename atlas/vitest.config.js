import { defineConfig, mergeConfig } from 'vitest/config'
import { createVitestConfig } from '@lynx-js/react/testing-library/vitest-config'

const defaultConfig = await createVitestConfig()
const config = defineConfig({
  test: {},
  plugins: [
    {
      name: 'force-full-reload',
      handleHotUpdate({ file, server }) {
        if (file.endsWith('.tsx') || file.endsWith('.ts') || file.endsWith('.jsx') || file.endsWith('.js')) {
          server.ws.send({ type: 'full-reload' });
        }
      },
    },
  ],
})

export default mergeConfig(defaultConfig, config)

