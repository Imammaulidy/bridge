module.exports = {
  apps: [
    {
      name: "bridge",
      script: "bridge.py",
      interpreter: "python3",
      autorestart: true,
      watch: false,
      max_memory_restart: "150M",
      restart_delay: 3000,
      max_restarts: 10,
      env: {
        PYTHONUNBUFFERED: "1",
        RISH_APPLICATION_ID: "com.termux"
      }
    }
  ]
};
