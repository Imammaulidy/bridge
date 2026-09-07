module.exports = {
  apps: [
    {
      name: "bridge",
      script: "bridge.py",
      interpreter: "python",
      autorestart: true,
      watch: false,
      max_memory_restart: "150M",
      env: {
        PYTHONUNBUFFERED: "1"
      }
    }
  ]
};
