# syntax=docker/dockerfile:1
# ifc-ruhsat — uzak MCP sunucusu (streamable HTTP, yol /mcp)
ARG PYTHON_IMAGE=public.ecr.aws/docker/library/python:3.12-slim

FROM ${PYTHON_IMAGE} AS derleme
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv
RUN pip install uv
WORKDIR /src
# Önce yalnız bağımlılıklar (IfcOpenShell tekerleği dahil): kaynak değişince bu katman önbellekte kalır
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY README.md LICENSE KAYNAKLAR.md CHANGELOG.md ./
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable \
 && /opt/venv/bin/ifc-ruhsat --version \
 && /opt/venv/bin/python -c "import ifcopenshell, ifcopenshell.geom; print('IfcOpenShell', ifcopenshell.version)"

FROM ${PYTHON_IMAGE}
LABEL org.opencontainers.image.source="https://github.com/BerkantACUN/ifc-ruhsat" \
      org.opencontainers.image.description="Yapı ruhsatı IFC modeli yönetmelik kontrolü — MCP sunucusu (streamable HTTP)" \
      org.opencontainers.image.licenses="MIT"
RUN groupadd --system --gid 10001 ifc \
 && useradd --system --uid 10001 --gid ifc --no-create-home --shell /usr/sbin/nologin ifc
COPY --from=derleme /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    IFC_RUHSAT_HOST=0.0.0.0 \
    IFC_RUHSAT_PORT=8080
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["ifc-ruhsat"]
CMD ["mcp", "--http"]
