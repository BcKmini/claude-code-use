FROM rust:bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        libssl-dev \
        pkg-config \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

ENV CARGO_TERM_COLOR=always
WORKDIR /workspace

# Pre-fetch dependencies so layer is cached
COPY rust/Cargo.toml rust/Cargo.lock ./rust/
RUN cd rust && cargo fetch --locked 2>/dev/null || true

# Copy full source
COPY . .

RUN cd rust && cargo build --workspace --release \
    && cp target/release/claude-tools /usr/local/bin/claude-tools

CMD ["bash"]
