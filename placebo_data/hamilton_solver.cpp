// Hamilton Loop Solver for q9.py grids
// Compile: g++ -O3 -o hamilton_solver hamilton_solver.cpp
// Run: hamilton_solver.exe <subpass>

#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <cstring>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <utility>

using namespace std;

const int GRID_SIZE = 16;
const int dx[] = {1, 0, -1, 0};  // right, up, left, down
const int dy[] = {0, 1, 0, -1};

bool walkable[GRID_SIZE + 2][GRID_SIZE + 2];  // 1-indexed with padding
bool visited[GRID_SIZE + 2][GRID_SIZE + 2];
int total_walkable = 0;
int visited_count = 0;
long long iterations = 0;
const long long MAX_ITERATIONS = 10000000000LL;  // 10 billion
bool timed_out = false;

int start_x, start_y;
vector<pair<int, int>> path;

uint64_t affected_stamp[GRID_SIZE + 2][GRID_SIZE + 2];
uint64_t stamp_id = 1;

struct Move {
    int group;
    int warn_score;
    int len;
    int dir;
};

inline int count_unvisited_neighbors(int x, int y) {
    int count = 0;
    for (int d = 0; d < 4; d++) {
        int nx = x + dx[d], ny = y + dy[d];
        if (walkable[nx][ny] && !visited[nx][ny]) count++;
    }
    return count;
}

// Check if removing cells would create a dead end
// Only checks neighbors of removed cells
bool would_create_dead_end(int x, int y, int dir, int len) {
    // Mark cells as temporarily visited
    int cx = x, cy = y;
    for (int i = 0; i < len; i++) {
        cx += dx[dir];
        cy += dy[dir];
        visited[cx][cy] = true;
        visited_count++;
    }

    int remaining = total_walkable - visited_count;
    bool dead_end = false;

    if (remaining > 0) {
        ++stamp_id;
        if (stamp_id == 0) {
            memset(affected_stamp, 0, sizeof(affected_stamp));
            stamp_id = 1;
        }

        pair<int, int> affected[(GRID_SIZE * 4) + 8];
        int affected_count = 0;

        cx = x;
        cy = y;
        for (int i = 0; i < len; i++) {
            cx += dx[dir];
            cy += dy[dir];
            for (int d = 0; d < 4; d++) {
                int nx = cx + dx[d], ny = cy + dy[d];
                if (walkable[nx][ny] && !visited[nx][ny]) {
                    if (affected_stamp[nx][ny] != stamp_id) {
                        affected_stamp[nx][ny] = stamp_id;
                        if (affected_count < (int)(sizeof(affected) / sizeof(affected[0]))) {
                            affected[affected_count++] = {nx, ny};
                        }
                    }
                }
            }
        }

        for (int i = 0; i < affected_count; i++) {
            int ax = affected[i].first;
            int ay = affected[i].second;
            int neighbor_count = count_unvisited_neighbors(ax, ay);
            if (neighbor_count == 0) {
                dead_end = true;
                break;
            }
            if (neighbor_count == 1) {
                // Only OK if it's start position or very few cells left
                if (ax != start_x || ay != start_y) {
                    if (remaining > 2) {
                        dead_end = true;
                        break;
                    }
                }
            }
        }
    }

    // Restore
    cx = x + dx[dir] * len;
    cy = y + dy[dir] * len;
    for (int i = 0; i < len; i++) {
        visited[cx][cy] = false;
        visited_count--;
        cx -= dx[dir];
        cy -= dy[dir];
    }

    return dead_end;
}

bool dfs(int x, int y) {
    if (timed_out) return false;
    iterations++;
    if (iterations > MAX_ITERATIONS) {
        timed_out = true;
        return false;
    }
    
    if ((iterations & 0xFFFFFF) == 0) {
        cerr << "Iterations: " << iterations / 1000000 << "M, path: " << path.size() 
             << "/" << total_walkable << endl;
    }
    
    if (visited_count == total_walkable) {
        // Check if adjacent to start
        for (int d = 0; d < 4; d++) {
            if (x + dx[d] == start_x && y + dy[d] == start_y) {
                return true;
            }
        }
        return false;
    }
    
    // Generate moves - use Warnsdorff's heuristic combined with long runs
    // Warnsdorff: prefer cells with fewer unvisited neighbors (less likely to create dead ends)
    Move moves[64];
    int move_count = 0;
    
    for (int d = 0; d < 4; d++) {
        int cx = x, cy = y;
        int run_len = 0;
        while (true) {
            cx += dx[d];
            cy += dy[d];
            if (walkable[cx][cy] && !visited[cx][cy]) {
                run_len++;
            } else {
                break;
            }
        }
        
        if (run_len == 0) continue;
        
        auto try_add = [&](int len, int group) {
            if (move_count >= (int)(sizeof(moves) / sizeof(moves[0]))) return;
            if (would_create_dead_end(x, y, d, len)) return;
            int ex = x + dx[d] * len;
            int ey = y + dy[d] * len;
            int warn_score = count_unvisited_neighbors(ex, ey);
            moves[move_count++] = {group, warn_score, len, d};
        };
        
        try_add(run_len, 0);
        if (run_len > 1) {
            try_add(1, 1);
            for (int len = 2; len < run_len; len++) {
                try_add(len, 2);
            }
        }
    }
    
    sort(moves, moves + move_count, [](const Move& a, const Move& b) {
        if (a.group != b.group) return a.group < b.group;
        if (a.warn_score != b.warn_score) return a.warn_score < b.warn_score;
        return a.len > b.len;
    });
    
    for (int mi = 0; mi < move_count; mi++) {
        const Move& move = moves[mi];
        
        // Apply move
        int cx = x, cy = y;
        for (int i = 0; i < move.len; i++) {
            cx += dx[move.dir];
            cy += dy[move.dir];
            visited[cx][cy] = true;
            visited_count++;
            path.push_back({cx, cy});
        }
        
        if (dfs(cx, cy)) {
            return true;
        }
        
        // Backtrack
        for (int i = 0; i < move.len; i++) {
            visited[cx][cy] = false;
            visited_count--;
            path.pop_back();
            cx -= dx[move.dir];
            cy -= dy[move.dir];
        }
        
        if (timed_out) return false;
    }
    
    return false;
}

void parse_map(const string& map_str) {
    memset(walkable, false, sizeof(walkable));
    memset(visited, false, sizeof(visited));
    total_walkable = 0;
    
    vector<string> lines;
    string line;
    for (char c : map_str) {
        if (c == '\n') {
            if (!line.empty()) {
                // Trim leading/trailing whitespace
                size_t start = line.find_first_not_of(" \t");
                if (start != string::npos) {
                    line = line.substr(start);
                }
                if (!line.empty()) {
                    lines.push_back(line);
                }
            }
            line.clear();
        } else {
            line += c;
        }
    }
    if (!line.empty()) {
        size_t start = line.find_first_not_of(" \t");
        if (start != string::npos) {
            line = line.substr(start);
        }
        if (!line.empty()) {
            lines.push_back(line);
        }
    }
    
    for (int row_idx = 0; row_idx < (int)lines.size() && row_idx < GRID_SIZE; row_idx++) {
        int y = GRID_SIZE - row_idx;  // Flip: top row = 16, bottom = 1
        for (int x_idx = 0; x_idx < (int)lines[row_idx].size() && x_idx < GRID_SIZE; x_idx++) {
            if (lines[row_idx][x_idx] == '.') {
                int x = x_idx + 1;  // 1-indexed
                walkable[x][y] = true;
                total_walkable++;
            }
        }
    }
    
    cout << "Total walkable cells: " << total_walkable << endl;
}

int main(int argc, char* argv[]) {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    if (argc < 2) {
        cerr << "Usage: hamilton_solver <subpass>" << endl;
        return 1;
    }
    
    int subpass = atoi(argv[1]);
    
    // Maps for subpasses 4, 5, 6
    const char* maps[] = {
        "", "", "", "",
        // SubPass 4
        "................\n"
        "................\n"
        "................\n"
        "................\n"
        "...............\n"
        "................\n"
        "................\n"
        "................\n"
        "................\n"
        "................\n"
        "................\n"
        "................\n"
        "..X.............\n"
        "..X.............\n"
        "................\n"
        "................\n",
        // SubPass 5
        "  ................\n"
        "..X.........X...\n"
        "........X......X\n"
        "................\n"
        "..X...X..X......\n"
        "........X.......\n"
        "................\n"
        "............X...\n"
        ".....X.....X..XX\n"
        "................\n"
        "............X...\n"
        "......X.....X...\n"
        "................\n"
        "................\n"
        "............X.X.\n"
        "................\n",
        // SubPass 6
        "................\n"
        "................\n"
        "...........X....\n"
        "................\n"
        ".....XX.........\n"
        "................\n"
        "................\n"
        "......X.........\n"
        "...X............\n"
        "................\n"
        "...X..X.....X...\n"
        "......X.........\n"
        "................\n"
        "............X...\n"
        "................\n"
        "................\n"
    };
    
    if (subpass < 4 || subpass > 6) {
        cerr << "Subpass must be 4, 5, or 6" << endl;
        return 1;
    }
    
    parse_map(maps[subpass]);
    
    // Find starting cell (minimum coordinate)
    start_x = 0; start_y = 0;
    for (int x = 1; x <= GRID_SIZE; x++) {
        for (int y = 1; y <= GRID_SIZE; y++) {
            if (walkable[x][y]) {
                if (start_x == 0) {
                    start_x = x;
                    start_y = y;
                } else if (x < start_x || (x == start_x && y < start_y)) {
                    start_x = x;
                    start_y = y;
                }
            }
        }
    }
    
    cout << "Starting at: (" << start_x << ", " << start_y << ")" << endl;
    
    path.reserve(total_walkable);
    visited[start_x][start_y] = true;
    visited_count = 1;
    path.push_back({start_x, start_y});
    
    auto start_time = chrono::high_resolution_clock::now();
    
    bool solved = dfs(start_x, start_y);
    
    auto end_time = chrono::high_resolution_clock::now();
    auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
    
    cout << "Time: " << duration.count() / 1000.0 << " seconds" << endl;
    cout << "Iterations: " << iterations << endl;
    
    if (solved) {
        cout << "SOLVED! Path length: " << path.size() << endl;
        cout << "Steps (for q9.py):" << endl;
        cout << "[";
        for (int i = 1; i < (int)path.size(); i++) {
            if (i > 1) cout << ", ";
            cout << "{\"xy\": [" << path[i].first << ", " << path[i].second << "]}";
        }
        cout << "]" << endl;
    } else {
        if (iterations >= MAX_ITERATIONS) {
            cout << "TIMEOUT - exceeded iteration limit" << endl;
        } else {
            cout << "NO SOLUTION FOUND" << endl;
        }
    }
    
    return solved ? 0 : 1;
}
