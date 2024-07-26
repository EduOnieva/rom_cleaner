echo "Running the rom_cleaner..."

echo "Building the docker image..."
docker build -t rom_cleaner:latest .

echo "Running the docker image..."
docker run -it --name rom_cleaner --rm rom_cleaner  --regions=$1 --url=$2

echo "Done!"