{ pkgs, lib, config, inputs, ... }:

let
  system = pkgs.system;
  cmsPackage = inputs.aoi-cms-nix.packages.${system}.cms.override { useNixPaths = true; };
  cmsAOIPackage = inputs.cms-aoi-import.packages.${system}.default.override { cms = cmsPackage; python = inputs.aoi-cms-nix.packages.${system}.pythonForCMS; };
  isolateEnv = inputs.aoi-cms-nix.packages.${system}.isolate-environment.override {
    enablePython3 = false;
    enableRust = false;
    enableCsharp = false;
  };
  testTasks = "${inputs.aoi-cms-nix}/flakeparts/test-tasks";
in

{
  # https://devenv.sh/packages/
  packages = [ pkgs.git pkgs.postgresql.pg_config pkgs.watchexec cmsPackage cmsAOIPackage ];

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

   files."$DEVENV_STATE/config/backend-dev.yaml".yaml = {
      database_uri = "postgresql:///aoi-portal";
      secret_key = "Please change me";
      session_token_key = "UZb1zOeZtEw1fsWhRftFE0AqSVTLAouZzFwt5cwiqSo=";
      debug = true;
      # same as to aoi-contestant-pc-control:keys/test-jwt-pub.peb
      proxy_auth_public_key = ''
        -----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArDUS/q3qMXTs8Xec3kcd
        xJgI+ia0hYZlvvH7357ri/seuJogpjUJ3egT3wHWC7wUjRlUzJvjPJQTVvaPRq05
        gmYF0ZROUOYRmjqJ8/A+K6iE8GP1hvIvaWekwUcC9FVG/MdCkFYlQJdeTYj6poUT
        XZLlu/MZ7CUWAqqh0KJVES4cWOLiQ12B0l0t9E1sdw1MlsnAkW9eKmFOBfK6YLJs
        a8V921TN9e2QlUyZITdGVFpSXnZgntRc5ApG7UTpUeXqw6Ewh6A+RMX3z8e6umpd
        LRKMLZeiQpfEtvO9oDvkdSxs7FS6WKxiRWf9o1q0PdZ7FOEweCOnxeazT36a3Nvn
        EwIDAQAB
        -----END PUBLIC KEY-----
      '';
      cms = {
        database_uri = "postgresql+psycopg2:///cmsuser";
        evaluation_service = {
          host = "localhost";
          port = 25000;
        };
      };
   };

   files."$DEVENV_STATE/config/cms.conf".json = {
      core_services = {
        LogService = [["localhost" 29000]];
        ResourceService = [["localhost" 28000]];
        ScoringService = [["localhost" 28500]];
        Checker = [["localhost" 22000]];
        EvaluationService = [["localhost" 25000]];
        ContestWebServer = [["localhost" 21000]];
        AdminWebServer = [["localhost" 21100]];
        ProxyService = [["localhost" 28600]];
        Worker = [["localhost" 26000]];
      };
      other_services = {};
      database = "postgresql+psycopg2:///cmsuser";
      log_dir = "${config.devenv.state}/cms/log";
      data_dir = "${config.devenv.state}/cms/lib";
      cache_dir = "${config.devenv.state}/cms/cache";
      run_dir = "${config.devenv.state}/cms/run";
      secret_key = "882de6ff9182a6e87b136f362aeefc68";
      sandbox_implementation = "stupid";
      cmsuser = builtins.getEnv "USER";
   };

  env = {
    CMS_CONFIG = "${config.devenv.state}/config/cms.conf";
  };

  # https://devenv.sh/processes/
  processes.backend = {
    cwd = "backend";
    exec = "watchexec -r -e py,yaml -- python3 run.py --config $DEVENV_STATE/config/backend-dev.yaml wsgi";
    after = ["db:init@completed" "cms:init@completed"];
  };

  processes.frontend = {
    exec = "npm run serve";
    cwd = "frontend";
  };

  processes.cmsLogService = {
    exec = ''
      exec ${cmsPackage}/bin/cmsLogService
    '';
    after = ["cms:init@completed"];
  };

  processes.cmsResourceService = {
    exec = ''
      export PATH="${isolateEnv}/bin:$PATH"
      exec ${cmsPackage}/bin/cmsResourceService -a ALL
    '';
    after = ["cms:init@completed"];
    ready = {
      http.get = {
        port = 8889;
      };
      initial_delay = 5;
      period = 2;
    };
  };
  
  # https://devenv.sh/services/
  services.postgres.enable = true;
  services.postgres.initialDatabases = [
    { name = "aoi-portal"; }
    { name = "cmsuser"; }
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

  tasks."cms:init" = {
    exec = ''
      set -eu
      mkdir -p "$DEVENV_STATE/cms"/{log,lib,cache,run}

      if [ ! -f "$DEVENV_STATE/cms_initialized" ]; then
        echo "🔧 Initializing CMS database..."

        ${cmsPackage}/bin/cmsInitDB
        ${cmsPackage}/bin/cmsAddAdmin -p password1 admin

        # Import placeholder contest
        tmpdir=$(mktemp -td cmsinit-XXXXXXXX)
        mkdir -p "$tmpdir/contest"
        cat > "$tmpdir/contest/contest.yaml" <<'CONTESTEOF'
      {"name": "dev", "description": "Development Contest", "tasks": {}, "token_mode": "infinite"}
      CONTESTEOF
        ${cmsPackage}/bin/cmsImportContest "$tmpdir/contest"
        rm -rf "$tmpdir"

        # Set languages to C++ only
        psql -d cmsuser -c "UPDATE contests SET languages = ARRAY['C++20 / g++'] WHERE id = 1;"

        # Add test user and participation
        ${cmsPackage}/bin/cmsAddUser -p password1 T Rainer trainer
        ${cmsPackage}/bin/cmsAddParticipation -c 1 trainer

        touch "$DEVENV_STATE/cms_initialized"
        echo "✅ CMS initialized successfully!"
      else
        echo "✓ CMS already initialized"
      fi
    '';
    after = [ "devenv:processes:postgres@ready" ];
  };

  tasks."cms:import-tasks" = {
    exec = ''
      set -eu
      if [ ! -f "$DEVENV_STATE/cms_tasks_imported" ]; then
        echo "📦 Importing test tasks..."
        rm -rf "$DEVENV_STATE/cms_tasks"
        cp -r --no-preserve=mode ${testTasks} "$DEVENV_STATE/cms_tasks"
        ${cmsAOIPackage}/bin/cmsAOI upload -c1 $DEVENV_STATE/cms_tasks/helloworld
        ${cmsAOIPackage}/bin/cmsAOI upload -c1 $DEVENV_STATE/cms_tasks/communication
        touch "$DEVENV_STATE/cms_tasks_imported"
        echo "✅ Test tasks imported!"
      else
        echo "✓ Test tasks already imported"
      fi
    '';
    after = ["cms:init@completed" "devenv:processes:cmsResourceService@ready"];
  };

  # See full reference at https://devenv.sh/reference/options/

  process.manager.implementation = "process-compose";
}
