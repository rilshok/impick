# ImPick Server

The ImPick Server is a web application that allows users to view and select images from different groups. It is built using [FastAPI](https://fastapi.tiangolo.com/) and [image-picker](https://rvera.github.io/image-picker/).

## Features

- Sequential or individual mode for viewing groups of images
- Selection of one images from each group
- CSV reporting of selected images

## Prerequisites

Python 3.7 or higher

## Installation

Clone the repository:

```bash
git clone git@github.com:rilshok/impick.git
pip install -e impick
```

or install it from pip

```bash
pip install impick
```

## Usage

To run the ImPick Server, follow these steps:

### Prepare your image groups:

- Create a directory for each image group.
- Place the images for each group in their respective directories.

### Start the server:

- Open a terminal or command prompt.
- Run the following command:

```bash
impick_server --images-root <path-to-image-groups-directory> --report-file <path-to-report-file.csv> --mode {individual|sequential} --host <host> --port <port>
```

Replace <path-to-image-groups-directory> with the path to the directory containing your image groups, and <path-to-report-file.csv> with the desired path to the CSV file for reporting the selected images.

For example:

```bash
impick_server --images-root ~/images --report-file ~/impick-report.csv --mode individual --host localhost --port 8000
```

### Access the web interface:

Open a web browser.
Visit [http://localhost:8000/](http://localhost:8000) (or the specified host and port if different) to start viewing and selecting images.

**Note:** When the server is running in the `individual` mode, each user will view and select their own set of images. In the `sequential` mode, all users will view the image groups one by one.

The root path (/) of the server sets the path value in the report to `anonym`. Navigating to any other path will update the report with the corresponding path value. The image selection process is based on the selected server mode.

## Screenshots
<!-- screenshots here to illustrate the usage of the server -->

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
