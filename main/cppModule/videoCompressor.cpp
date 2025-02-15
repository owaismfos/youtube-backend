#include <iostream>
#include <cstdlib>
#include <cstdio>
#include <sstream>

using namespace std;

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cerr << "Usage: " << argv[0] << " <input_file> <output_file>" << endl;
        return 1;
    }

    string inputFile = argv[1];
    string outputFile = argv[2];

    // FFmpeg command to compress video
    string command = "ffmpeg -i " + inputFile + " -vf scale=1024:-2 -vcodec libx264 -crf 28 -progress pipe:1 -nostats " + outputFile;

    FILE* pipe = popen(command.c_str(), "r");
    if (!pipe) {
        cerr << "Failed to start FFmpeg process!" << endl;
        return 1;
    }

    char buffer[256];
    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        string line(buffer);
        // Exraction of progress from FFmpeg output
        if (line.find("out_time=") != string::npos) {
            string timeStr = line.substr(line.find("out_time=") + 1);
            cout << "Progress: " << timeStr << endl;
            cout.flush();
        }
    }
    int result = pclose(pipe);

    if (result == 0) {
        cout << "Video compression successful!" << endl;
    } else {
        cerr << "Video compression failed!" << endl;
    }

    return result;
}