#pragma once

// 一个顺子、刻子或杠子 
struct meld_info {
	int x, y, z;
	meld_info(int x1 = -1, int y1 = -1, int z1 = -1) : x(x1), y(y1), z(z1) { }
	meld_info& operator=(const meld_info& rhs) {
		this->x = rhs.x;
		this->y = rhs.y;
		this->z = rhs.z;

		return *this;
	}
};

class compare_meld {
public:
	bool compare_meld::operator () (const meld_info m1, const meld_info m2) const {
		return m1.x < m2.x;
	}
};

void gen_1_with_eyes();
void gen_2_with_eyes();

void gen_1_no_eyes();
void gen_2_no_eyes();

void save_data();
