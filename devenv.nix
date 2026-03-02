{ pkgs, lib, config, inputs, ... }:

{
  # https://devenv.sh/packages/
  packages = [ pkgs.git pkgs.postgresql.pg_config pkgs.watchexec ];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    directory = "./backend";

    venv.enable = true;
    venv.requirements = builtins.readFile ./backend/requirements.txt + builtins.readFile ./backend/requirements_dev.txt;
  };
  languages.javascript = {
    enable = true;
    directory = "./frontend";
    package = pkgs.nodejs-slim_22;    # downgrade from 24 to 22: @achrinza/node-ipc@9.2.9 says it only supports up to 22
    npm.enable = true;
    npm.install.enable = true;
  };
  languages.typescript.enable = true;

  # https://devenv.sh/reference/options/#files
  files."$DEVENV_STATE/config/backend-dev.yaml" = {
    yaml = {
      database_uri = "postgresql:///aoi-portal";
      secret_key = "Please change me";
      session_token_key = "UZb1zOeZtEw1fsWhRftFE0AqSVTLAouZzFwt5cwiqSo=";
      debug = true;
    };
  };

  # https://devenv.sh/processes/
  processes.backend = {
    cwd = "backend";
    exec = "watchexec -r -e py,yaml -- python3 run.py --config $DEVENV_STATE/config/backend-dev.yaml wsgi";
    after = ["db:init@completed"];
  };

  processes.frontend = {
    exec = "npm run serve";
    cwd = "frontend";
  };
  
  # https://devenv.sh/services/
  services.postgres.enable = true;
  services.postgres.initialDatabases = [
    { name = "aoi-portal"; }
  ];

  # https://devenv.sh/tasks/
  tasks."db:init" = {
    exec = ''
      set -eu
      if [ ! -f $DEVENV_STATE/db_initialized ]; then
        echo "🔧 Initializing database for the first time..."
        cd backend
        python3 run.py --config $DEVENV_STATE/config/backend-dev.yaml createdb
        python3 run.py --config $DEVENV_STATE/config/backend-dev.yaml addadmin --first-name Theodor --last-name Rainer --password password1 --email t.rainer@example.org
        touch $DEVENV_STATE/db_initialized
        echo "✅ Database initialized successfully!"
      else
        echo "✓ Database already initialized"
      fi
    '';
    after = [ "devenv:processes:postgres@ready" ];
  };

  # See full reference at https://devenv.sh/reference/options/
}
