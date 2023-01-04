module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:8000/'],
    },
    assert: {
      assertions: {
        "categories:accessibility": ["error", {"minScore": 1}]
      }
    }
  },
};
