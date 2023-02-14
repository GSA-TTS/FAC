module.exports = {
  ci: {
    collect: {
      settings: {
        hostname: '127.0.0.1'
      },
      url: ['http://localhost:8000/'],
    },
    assert: {
      assertions: {
        "categories:accessibility": ["error", {"minScore": .98}]
      }
    }
  },
};
