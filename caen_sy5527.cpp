#include <unistd.h>
#include <string.h>
#include <iostream>
#include <csignal>
#include <cstdlib>
#include <string>
#include <CAENHVWrapper.h>
#include <regex>
#include <sys/socket.h>
#include <sys/poll.h>
#include <netinet/in.h>
#include <array>
#include <algorithm>
#include <numeric>

static volatile std::sig_atomic_t gSignalStatus = 0;

void interrupt(int signal) {
    std::cout << "\nReceived signal " << signal << '\n';
    gSignalStatus = signal;
}

using std::string;
using std::stoi;
using std::stof;

string AddCommas(std::array<float, 12>& a) {
    return std::accumulate(a.begin(), a.end(), std::to_string(a.front()),
            [](string a, float b) {return std::move(a) + ',' + std::to_string(b);});
}

string AddCommas(std::array<int, 12>& a) {
    return std::accumulate(a.begin(), a.end(), std::to_string(a.front()),
            [](string a, int b) {return std::move(a) + ',' + std::to_string(b);});
}

int main(int argc, char** argv) {
    std::signal(SIGINT, interrupt);
    std::signal(SIGTERM, interrupt);
    std::signal(SIGCHLD, SIG_IGN);
    //std::signal(SIGPIPE, SIG_IGN);

    if (argc != 3) {
        std::cout << "Usage: " << argv[0] << " port caen_ip\n";
        return 0;
    }

    std::cout << "Starting\n";

    int server_fd, client_fd, portnum, handle, ch_nr;

    struct sockaddr_in server_addr, client_addr;
    int opt = 1, i, bytes_read;
    socklen_t server_len = sizeof(server_addr), client_len = sizeof(client_addr);
    char buffer[1024];
    std::array<float, 12> float_val;
    std::array<int, 12> int_val;
    unsigned short sl;
    std::array<unsigned short, 12> ch;
    string ch_s, task, value, msg;

    pollfd poll_obj;

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        std::cout << "Could not create socket\n";
        return 1;
    }
    memset(&server_addr, 0, sizeof(server_addr));
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        std::cout << "Could not setup socket\n";
        return 1;
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(atoi(argv[1]));

    if (bind(server_fd, (sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cout << "Could not bind to address\n";
        close(server_fd);
        return 2;
    }

    listen(server_fd, 4); // accept 4 connections

    std::regex set_re("set ch([1-9]?[0-9]) sl([0-3]) "
            "(vset|rup|rdn|tripi|tript|pw|pon|pdn) "
            "([+-]?[1-9][0-9]*(?:\\.[0-9]+)?(?:[eE][+\\-]?[1-9]*[0-9])?)",
	    std::regex_constants::ECMAScript | std::regex_constants::optimize);
    std::regex get_re("get ch([1-9]?[0-9]) sl([0-3]) "
            "(vmon|imon|vset|stat|rup|rdn|tripi|tript|pw|pon|pdn)",
            std::regex_constants::extended | std::regex_constants::optimize);

    int err = CAENHV_InitSystem(SY5527, 0, argv[2], "admin", "admin", &handle);
    if (err != 0) {
        std::cout << "Could not connect to HV crate. Error " << err << '\n';
        close(server_fd);
    }
    std::cout << "Setup completed\n";
    while (gSignalStatus == 0) {
        poll_obj.fd = server_fd;
        poll_obj.events = POLLIN;
        i = poll(&poll_obj, 1, 1000);

        if (i == 0) continue;
        else if (i < 0) {
            std::cout << "Error " << i << " from poll\n";
            break;
        }

        if (poll_obj.revents & POLLIN) {
            if ((client_fd = accept(server_fd, (sockaddr*)&client_addr, &client_len)) == -1) {
                std::cout << "Error accepting connection\n";
            }
        } else {
            continue;
        }

        bytes_read = read(client_fd, buffer, sizeof(buffer));
        msg.assign(buffer, bytes_read);

        std::smatch match;
        string payload;
        std::cout << "Got " << msg << '\n';
        if (std::regex_match(msg, match, set_re)) {
            ch[0] = stoi((string)match.str(1));
            sl = stoi((string)match.str(2));
            task = match.str(3);
            value = match.str(4);
            payload = "OK;";
            if (task == "vset") {
                float_val[0] = stof(value);
                err = CAENHV_SetChParam(handle, sl, "V0Set", 1, ch.data(),
                        float_val.data());
            } else if (task == "pw") {
                int_val[0] = stoi(value);
                err = CAENHV_SetChParam(handle, sl, "Pw", 1, ch.data(),
                        int_val.data());
            } else if (task == "rup") {
                float_val[0] = stof(value);
                err = CAENHV_SetChParam(handle, sl, "RUp", 1, ch.data(),
                        float_val.data());
            } else if (task == "rdn") {
                float_val[0] = stof(value);
                err = CAENHV_SetChParam(handle, sl, "RDWn", 1, ch.data(),
                        float_val.data());
            } else if (task == "tripi") {
                float_val[0] = stof(value);
                err = CAENHV_SetChParam(handle, sl, "I0Set", 1, ch.data(),
                        float_val.data());
            } else if (task == "tript") {
                float_val[0] = stof(value);
                err = CAENHV_SetChParam(handle, sl, "Trip", 1, ch.data(),
                        float_val.data());
            } else if (task == "pon") {
                int_val[0] = stoi(value);
                err = CAENHV_SetChParam(handle, sl, "POn", 1, ch.data(),
                        int_val.data());
            } else if (task == "pdn") {
                int_val[0] = stoi(value);
                err = CAENHV_SetChParam(handle, sl, "PDwn", 1, ch.data(),
                        int_val.data());
            } else {
                payload = "ERR;01";
            }
        } else if (std::regex_match(msg, match, get_re)) {
            payload = "OK;";
	    ch[0] = stoi((string)match.str(1));
            sl = stoi((string)match.str(2));
            task = match.str(3);
            if (task == "vset") {
                err = CAENHV_GetChParam(handle, sl, "V0Set", 1, ch.data(),
                        float_val.data());
                payload += std::to_string(float_val[0]);
            } else if (task == "vmon") {
		err = CAENHV_GetChParam(handle, sl, "VMon", 1, ch.data(),
                        float_val.data());
		std::cout << typeid(err).name() << "  " << err << '\n';
                payload += std::to_string(float_val[0]);
	    } else if (task == "imon") {
                err = CAENHV_GetChParam(handle, sl, "IMon", 1, ch.data(),
                        float_val.data());
           	payload += std::to_string(float_val[0]); 
	    } else if (task == "stat") {
                err = CAENHV_GetChParam(handle, sl, "Status", 1, ch.data(),
                        int_val.data());
		payload += std::to_string(int_val[0]);
            } else if (task == "rup") {
                err = CAENHV_GetChParam(handle, sl, "RUp", 1, ch.data(),
                        float_val.data());
            	payload += std::to_string(float_val[0]);
	    } else if (task == "rdn") {
                err = CAENHV_GetChParam(handle, sl, "RDWn", 1, ch.data(),
                        float_val.data());
            	payload += std::to_string(float_val[0]);
	    } else if (task == "tripi") {
                err = CAENHV_GetChParam(handle, sl, "I0Set", 1, ch.data(),
                        float_val.data());
            	payload += std::to_string(float_val[0]);
	    } else if (task == "tript") {
                err = CAENHV_GetChParam(handle, sl, "Trip", 1, ch.data(),
                        float_val.data());
            	payload += std::to_string(float_val[0]);
	    } else if (task == "pw") {
                err = CAENHV_GetChParam(handle, sl, "Pw", 1, ch.data(),
                        int_val.data());
            	payload += std::to_string(int_val[0]);
	    } else if (task == "pon") {
                err = CAENHV_GetChParam(handle, sl, "POn", 1, ch.data(),
                        int_val.data());
            	payload += std::to_string(int_val[0]);
	    } else if (task == "pdn") {
                err = CAENHV_GetChParam(handle, sl, "PDwn", 1, ch.data(),
                        int_val.data());
            	payload += std::to_string(int_val[0]);
	    } else {
                payload = "ERR;01";
            }
        } else {
            payload = "ERR;00";
        }
        std::cout << "Payload: " << payload << '\n';
        if (err != 0) payload = "ERR;c" + std::to_string(err);
        payload += "\r\n";
        i = send(client_fd, payload.data(), payload.size(), MSG_NOSIGNAL);
        if (i == EPIPE) {
            std::cout << "Got a SIGPIPE error from " << msg << "\n";
        }
        close(client_fd);
    }
    std::cout << "Returning with code " << gSignalStatus << "\n";
    close(server_fd);
    err = CAENHV_DeinitSystem(handle);
    return 0;
}
