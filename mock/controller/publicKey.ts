import type { MockMethod } from 'vite-plugin-mock'

export default [
  {
    url: '/publicKey',
    method: 'get',
    response: () => ({
      code: 200,
      data: {
        publicKey: 'mock-public-key-for-demo',
      },
    }),
  },
] as MockMethod[]
