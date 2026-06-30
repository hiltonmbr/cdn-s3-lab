.DEFAULT_GOAL := help
.PHONY: help up down clean clean-data status shell-server setup-env jupyter-lab strip lint check test

help:
	@echo "🪣✨ Welcome to the S3 Lab! Your Object Storage playground! ✨🪣"
	@echo "🚀 Choose your adventure below:"
	@echo ""
	@echo "  🔥 make up            - 🏗️  Start RustFS (single node, 4 drives, Erasure Coding)"
	@echo "  🛑 make down          - 😴 Stop the server"
	@echo "  💣 make clean         - ☢️  Destroy containers, volumes, AND local data"
	@echo "  🧹 make clean-data    - 🗑️  Wipe only local downloads in temp/"
	@echo "  📡 make status        - 🔍 Show running containers"
	@echo "  🐚 make shell-server  - 👨‍💻 Open a shell on the RustFS container"
	@echo "  🐍 make setup-env     - 🪄  Create Python venv and install dependencies with uv"
	@echo "  📓 make jupyter-lab   - 🚀 Launch Jupyter Lab"
	@echo "  🧹 make strip         - ✂️  Strip all notebook outputs"
	@echo "  🔍 make check         - 🧪 Verify notebooks are output-stripped (CI-safe)"
	@echo "  🎨 make lint          - 🐍 Run ruff linter on src/ and notebooks/"
	@echo "  🧪 make test          - 🔬 Run pytest notebook tests (requires RustFS running)"
	@echo ""

up:
	@echo "🔥⚡ Starting RustFS with 4 drives and Erasure Coding... 🚀"
	docker compose up -d
	@echo ""
	@echo "🎉 Server is live!"
	@echo "   🌐 API endpoint:    http://localhost:9000"
	@echo "   🖥️  Admin Console:   http://localhost:9001  (admin / adminpassword)"
	@echo "   🧠 EC:4 drives — survives 2 drive failures"

down:
	@echo "😴 Stopping the server... 🌙"
	docker compose down

clean:
	@echo "💥☢️  NUKING everything! Containers, volumes, and local data! 💀"
	docker compose down -v
	rm -rf temp/*
	@echo "🧼 All clean!"

clean-data:
	@echo "🧹 Sweeping local downloads from temp/ (server untouched)..."
	rm -rf temp/*
	@echo "✅ temp/ is clean."

status:
	@echo "📡 Server status:"
	docker compose ps

shell-server:
	@echo "👨‍💻 Opening shell on rustfs-server..."
	docker exec -it rustfs-server /bin/sh

setup-env:
	@echo "🐍⚡ Creating Python environment with uv..."
	uv venv --clear
	uv sync
	uv run python -m ipykernel install --user --name=cdn-s3-lab --display-name="Python (cdn-s3-lab)"
	git config filter.nbstripout.smudge cat
	git config filter.nbstripout.clean "uv run python3 -c \"import sys,json; nb=json.load(sys.stdin); [c.update({'outputs':[],'execution_count':None}) for c in nb['cells'] if c.get('cell_type')=='code']; json.dump(nb, sys.stdout, indent=1, ensure_ascii=False)\""
	@echo "✅ Environment ready! Activate with: source .venv/bin/activate"
	@echo "✅ Jupyter kernel 'cdn-s3-lab' registered — select it in notebooks (don't use the generic 'Python 3')."

jupyter-lab:
	@echo "📓🚀 Launching Jupyter Lab..."
	uv run jupyter lab --notebook-dir=notebooks

strip:
	@echo "🧹 Stripping notebook outputs..."
	@for f in notebooks/*.ipynb; do \
		uv run python3 -c "import json,sys; f=sys.argv[1]; nb=json.load(open(f)); [c.update(outputs=[], execution_count=None) for c in nb['cells'] if c.get('cell_type')=='code']; json.dump(nb, open(f,'w'), indent=1, ensure_ascii=False); print('  ✓ '+f)" "$$f"; \
	done

check:
	@echo "🔍 Checking that all notebooks are output-stripped..."
	@uv run python3 -c "\
import json, glob, sys; \
failures = []; \
[failures.extend([(f, c.get('id','?')) for c in json.load(open(f))['cells'] if c.get('cell_type')=='code' and (c.get('outputs') or c.get('execution_count') is not None)]) for f in glob.glob('notebooks/*.ipynb')]; \
[print(f'  ❌ {f} cell {c} has outputs — run make strip') for f, c in failures] or print('  ✅ All notebooks are clean'); \
sys.exit(1 if failures else 0)"

lint:
	@echo "🎨 Running ruff linter..."
	uv run ruff check scripts/ notebooks/

test:
	@echo "🧪 Running notebook tests (RustFS must be running)..."
	uv run pytest tests/ --nbmake --nbmake-timeout=120 -v
