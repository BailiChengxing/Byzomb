from enum import Enum

class GunType(Enum):
    RIFLE = "步枪"
    MARKSMAN_RIFLE = "射手步枪"
    SNIPER = "狙击枪"
    SHOTGUN = "霰弹枪"
    SUBMACHINE_GUN = "冲锋枪"
    MACHINE_GUN = "机枪"
    LASER_GUN = "激光枪"
    PISTOL = "手枪"

class Gun:
    def __init__(self, name, gun_type, weight, mag_capacity, reserve_ammo, rate, speed ):
        """
        :param name: 枪支名称 (str)
        :param gun_type: 枪支类型 (GunType)
        :param weight: 重量 (int)
        :param mag_capacity: 主弹匣容量 (int)
        :param reserve_ammo: 副弹夹/备用弹药数量 (int)
        :param rate: 射速 (int)
        :param rate: 子弹速度 (int)
        :param mag_current: 当前弹夹 (int)
        """
        self.name = name
        self.gun_type = gun_type
        self.weight = weight
        self.mag_capacity = mag_capacity  # 弹匣上限
        self.current_mag = mag_capacity   # 当前弹匣内的子弹
        self.reserve_ammo = reserve_ammo  # 备用弹药（副弹夹）
        self.rate = rate
        self.speed =speed
        self.current_mag=mag_capacity

    def reload(self):
        """换弹逻辑"""
        needed = self.mag_capacity - self.current_mag
        if needed > 0 and self.reserve_ammo > 0:
            reload_amount = min(needed, self.reserve_ammo)
            self.current_mag += reload_amount
            self.reserve_ammo -= reload_amount
            print(f"[{self.name}] 换弹成功！当前子弹: {self.current_mag}/{self.reserve_ammo}")
        elif self.reserve_ammo <= 0:
            print(f"[{self.name}] 没弹药了！")
        else:
            print(f"[{self.name}] 弹匣已满。")
    def ls(self):
            info = (
                f"--- 武器详细参数 ---\n"
                f"当前弹夹： {self.current_mag}\n"
                f"名称: {self.name}\n"
                f"类型: {self.gun_type.value}\n"
                f"重量: {self.weight}kg\n"
                f"主弹夹: {self.mag_capacity}\n"
                f"副弹夹: {self.reserve_ammo}\n"
                f"射速: {self.rate}\n"
                f"子弹速度: {self.speed}\n"
                f"-------------------"
            )
            return info
    
if __name__ == "__main__":
    my_gun = Gun("AK47", GunType.RIFLE, 4.3, 30, 20,1,2)
    print(my_gun.ls())
    my_gun.current_mag-=30
    print(my_gun.ls())
    my_gun.reload()
    print(my_gun.ls())