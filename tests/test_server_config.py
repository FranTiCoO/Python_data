import importlib
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path


class ServerConfigTests(unittest.TestCase):
    def setUp(self):
        project_root = Path(__file__).resolve().parents[1]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        sys.modules.pop("server", None)
        sys.modules.pop("config", None)

        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.config_path = Path(self.temp_dir.name) / "config.py"
        self.config_path.write_text(
            "SENSOR_WAIT = 10\nSTATE_LIGHT = 1\n",
            encoding="utf-8",
        )

        self.fake_module = types.ModuleType("config")
        self.fake_module.__file__ = str(self.config_path)
        self.fake_module.SENSOR_WAIT = 10
        self.fake_module.STATE_LIGHT = 1
        sys.modules["config"] = self.fake_module

    def test_update_config_values_writes_valid_python(self):
        server_module = importlib.import_module("server")
        updated = server_module.update_config_file(
            {"SENSOR_WAIT": 15, "STATE_LIGHT": 0},
            config_path=str(self.config_path),
        )

        self.assertTrue(updated)
        content = self.config_path.read_text(encoding="utf-8")
        self.assertIn("SENSOR_WAIT = 15", content)
        self.assertIn("STATE_LIGHT = 0", content)

    def test_server_service_can_be_instantiated(self):
        server_module = importlib.import_module("server")
        service = server_module.Server()

        self.assertFalse(service.authenticated)

    def test_tls_material_generation_creates_ca_and_server_certs(self):
        base_path = Path(self.temp_dir.name)
        env_updates = {
            "RPC_TLS_CERT": str(base_path / "rpc-cert.pem"),
            "RPC_TLS_KEY": str(base_path / "rpc-key.pem"),
            "RPC_TLS_CA_CERT": str(base_path / "ca-cert.pem"),
            "RPC_TLS_CA_KEY": str(base_path / "ca-key.pem"),
        }
        previous = {key: os.environ.get(key) for key in env_updates}

        try:
            os.environ.update(env_updates)
            server_module = importlib.import_module("server")
            cert_path, key_path, ca_cert_path = server_module.ensure_tls_material(str(base_path))
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        self.assertTrue(Path(cert_path).exists())
        self.assertTrue(Path(key_path).exists())
        self.assertTrue(Path(ca_cert_path).exists())



if __name__ == "__main__":
    unittest.main()
