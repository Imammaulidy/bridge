module.exports = {
  apps: [
    {
      name: "bridge",
      script: "bridge.py",
      interpreter: "python",
      args: "3", // Mode Auto-Bridge (Standby memantau perintah dari Web POS)
      autorestart: true,
      watch: false,
      max_memory_restart: "150M",
      env: {
        PYTHONUNBUFFERED: "1"
      }
    }
  ]
};
