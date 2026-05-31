<template>
  <div class="total" :style="{ backgroundImage: `url(${bg})` }">
    <!-- <canvas class="rain"></canvas> -->
    <div class="sphere">
      <div class="sphere-bg" :style="{ backgroundImage: `url(${earth})` }"></div>
      <div class="sum" :style="{ backgroundImage: `url(${cloud})` }">
        <span>西海岸新区</span>
        <p>国际化城市治理大模型</p>
      </div>
    </div>
    <div class="cicle3" :style="{ backgroundImage: `url(${circle})` }"></div>
    <div class="cicle4" :style="{ backgroundImage: `url(${gqright})` }"></div>
    <div class="cicle5" :style="{ backgroundImage: `url(${gqleft})` }"></div>
    <div class="cicle6" :style="{ backgroundImage: `url(${gqbottomright})` }"></div>
    <div class="cicle7" :style="{ backgroundImage: `url(${gqbottomleft})` }"></div>
    <div class="cicle8" :style="{ backgroundImage: `url(${circle1})` }">
      <span>总体态势研判</span>
    </div>
    <div class="cicle9" :style="{ backgroundImage: `url(${circle2})` }">
      <span>
        社会管理
        <br />
        智能治理
      </span>
    </div>
    <div class="cicle10" :style="{ backgroundImage: `url(${circle1})` }">
      <span>
        经济运行
        <br />
        智能研判
      </span>
    </div>
    <div class="cicle11" :style="{ backgroundImage: `url(${circle2})` }">
      <span>
        城市治理
        <br />
        智能优化
      </span>
    </div>
  </div>
</template>

<script lang="ts" setup>
import gqbottomright from '/@/assets/data_screen_images/535gqbottomright.png'
import bg from '/@/assets/data_screen_images/53bg.png'
import cloud from '/@/assets/data_screen_images/53cloud.png'
import earth from '/@/assets/data_screen_images/53earth.png'
import gqbottomleft from '/@/assets/data_screen_images/53gqbottomleft.png'
import gqleft from '/@/assets/data_screen_images/53gqleft.png'
import gqright from '/@/assets/data_screen_images/53gqright.png'
import circle from '/@/assets/data_screen_images/circle.png'
import circle1 from '/@/assets/data_screen_images/circle1.png'
import circle2 from '/@/assets/data_screen_images/circle2.png'

defineOptions({
  name: 'DataScreenMap',
})

onMounted(() => {})
</script>

<style lang="scss" scoped>
@font-face {
  font-family: 'LCdd';
  src: url('../fonts/LCdd.TTF');
}
.total {
  position: relative;
  // float: left;
  top: -15%;
  width: 100%;
  height: 100%;
  background-size: 100% 100%;
}
.total .rain {
  position: absolute;
  top: 0;
  left: 0;
  z-index: -1;
}
.total .data1,
.total .data2,
.total .data3,
.total .data4 {
  position: absolute;
  width: 8rem;
  height: 4rem;
}

.total .data1 span,
.total .data2 span,
.total .data3 span,
.total .data4 span {
  // font-family: '宋体';
  font-size: 0.8rem;
  color: #0ac1c7;
}

.total .data1 p,
.total .data2 p,
.total .data3 p,
.total .data4 p {
  // font-family: 'LCdd';
  font-size: 1.5rem;
  color: #f29701;
}

.total .data1 {
  top: 12%;
  left: 10%;
}

.total .data2 {
  top: 3%;
  left: 42%;
}

.total .data3 {
  top: 5%;
  left: 62%;
}

.total .data4 {
  top: 28%;
  left: 73%;
}
.total .sphere {
  position: relative;
  width: 25rem;
  height: 25rem;
  margin: 14% auto 0;
}
.total .sphere .sphere-bg {
  position: absolute;
  top: 30%;
  left: 0;
  z-index: 100;
  width: 100%;
  height: 100%;
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
}
.total .sphere .sum {
  position: absolute;
  top: 30%;
  left: 0;
  z-index: 100;
  width: 100%;
  height: 100%;
  background-repeat: no-repeat;
  background-position: center;
  background-size: 55%;
}
.total .sphere .sum span {
  display: block;
  padding-left: 34%;
  margin-top: 35%;
  font-size: 1.5rem;
  color: #005a79;
}
.total .sphere .sum p {
  margin-top: 2%;
  // font-family: 'LCdd';
  font-size: 1.2rem;
  color: #003c63;
  text-align: center;
}
.total .cicle3 {
  position: absolute;
  top: 20%;
  left: 50%;
  width: 40rem;
  height: 40rem;
  background-repeat: no-repeat;
  background-position: center;
  background-size: 100%;
  transform: translateX(-50%) rotateX(75deg);
  animation: rotate3 20s linear infinite;
  transform-style: preserve-3d;
}

.total .cicle4 {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20rem;
  height: 20rem;
  background-repeat: no-repeat;
  background-position: center;
  background-size: 100%;
  transform: translateX(-50%) rotateX(75deg);
  animation: rotate3 2s linear infinite;
  transform-style: preserve-3d;
}

.total .cicle5 {
  position: absolute;
  top: 52%;
  left: 50%;
  width: 20rem;
  height: 20rem;
  background-repeat: no-repeat;
  background-position: center;
  background-size: 100%;
  transform: translateX(-50%) rotateX(75deg);
  animation: rotate4 2s linear infinite;
  transform-style: preserve-3d;
}

.total .cicle6 {
  position: absolute;
  top: 65%;
  left: 50%;
  width: 17rem;
  height: 17rem;
  background-repeat: no-repeat;
  background-position: center;
  background-size: 100%;
  transform: translateX(-50%) rotateX(75deg);
  animation: rotate3 2s linear infinite;
  transform-style: preserve-3d;
}

.total .cicle7 {
  position: absolute;
  top: 67%;
  left: 50%;
  width: 17rem;
  height: 17rem;
  background-repeat: no-repeat;
  background-position: center;
  background-size: 100%;
  transform: translateX(-50%) rotateX(75deg);
  animation: rotate4 2s linear infinite;
  transform-style: preserve-3d;
}

.total .cicle8,
.total .cicle9,
.total .cicle10,
.total .cicle11 {
  position: absolute;
  top: 40%;
  left: 50%;
  z-index: 100;
  width: 7rem;
  height: 7rem;
  margin-left: -2.5rem;
  border-radius: 50%;
}

.total .cicle8 span,
.total .cicle9 span,
.total .cicle10 span,
.total .cicle11 span {
  display: block;
  font-size: 1rem;
  font-weight: 800;
}
.total .cicle8 span {
  margin-top: 40%;
  margin-left: 8%;
}
.total .cicle9 span,
.total .cicle10 span,
.total .cicle11 span {
  margin-top: 35%;
  margin-left: 22%;
}

.total .cicle8 p,
.total .cicle9 p,
.total .cicle10 p,
.total .cicle11 p {
  font-size: 0.55rem;
  font-weight: 600;
  text-align: center;
  /* margin-top: 10%; */
}

.total .cicle8 {
  color: #f29701;
  background-repeat: no-repeat;
  background-size: 100%;
  animation: rotate5 20s linear infinite;
}

.total .cicle9 {
  color: #0ac1c7;
  background-repeat: no-repeat;
  background-size: 100%;
  animation: rotate6 20s linear infinite;
}

.total .cicle10 {
  color: #f29701;
  background-repeat: no-repeat;
  background-size: 100%;
  animation: rotate7 20s linear infinite;
}

.total .cicle11 {
  color: #0ac1c7;
  background-repeat: no-repeat;
  background-size: 100%;
  animation: rotate8 20s linear infinite;
}

@keyframes rotate {
  0% {
    transform: rotate(0);
  }

  100% {
    transform: rotate(360deg);
  }
}

@keyframes rotate2 {
  0% {
    transform: rotateX(75deg) rotateZ(0);
  }

  100% {
    transform: rotateX(75deg) rotateZ(360deg);
  }
}

@keyframes rotate3 {
  0% {
    transform: translateX(-50%) rotateX(75deg) rotateZ(0);
  }

  100% {
    transform: translateX(-50%) rotateX(75deg) rotateZ(360deg);
  }
}

@keyframes rotate4 {
  0% {
    transform: translateX(-50%) rotateX(75deg) rotateZ(0);
  }

  100% {
    transform: translateX(-50%) rotateX(75deg) rotateZ(-360deg);
  }
}

@keyframes rotate5 {
  0% {
    z-index: 100;
    transform: matrix3d(0.9, 0, 0, 0, 0, 0.9, 0, 0, 0, 0, 1, 0, 270, 0, 0, 1);
  }

  1% {
    z-index: 100.06279;
    transform: matrix3d(0.92093, 0, 0, 0, 0, 0.92093, 0, 0, 0, 0, 1, 0, 269.46722, 6.27905, 0, 1);
  }

  2% {
    z-index: 100.12533;
    transform: matrix3d(0.94178, 0, 0, 0, 0, 0.94178, 0, 0, 0, 0, 1, 0, 267.87097, 12.53332, 0, 1);
  }

  3% {
    z-index: 100.18738;
    transform: matrix3d(0.96246, 0, 0, 0, 0, 0.96246, 0, 0, 0, 0, 1, 0, 265.21756, 18.73813, 0, 1);
  }

  4% {
    z-index: 100.24869;
    transform: matrix3d(0.9829, 0, 0, 0, 0, 0.9829, 0, 0, 0, 0, 1, 0, 261.51745, 24.86899, 0, 1);
  }

  5% {
    z-index: 100.30902;
    transform: matrix3d(1.00301, 0, 0, 0, 0, 1.00301, 0, 0, 0, 0, 1, 0, 256.78526, 30.9017, 0, 1);
  }

  6% {
    z-index: 100.36812;
    transform: matrix3d(1.02271, 0, 0, 0, 0, 1.02271, 0, 0, 0, 0, 1, 0, 251.03965, 36.81246, 0, 1);
  }

  7% {
    z-index: 100.42578;
    transform: matrix3d(1.04193, 0, 0, 0, 0, 1.04193, 0, 0, 0, 0, 1, 0, 244.3033, 42.57793, 0, 1);
  }

  8% {
    z-index: 100.48175;
    transform: matrix3d(1.06058, 0, 0, 0, 0, 1.06058, 0, 0, 0, 0, 1, 0, 236.6028, 48.17537, 0, 1);
  }

  9% {
    z-index: 100.53583;
    transform: matrix3d(1.07861, 0, 0, 0, 0, 1.07861, 0, 0, 0, 0, 1, 0, 227.96854, 53.58268, 0, 1);
  }

  10% {
    z-index: 100.58779;
    transform: matrix3d(1.09593, 0, 0, 0, 0, 1.09593, 0, 0, 0, 0, 1, 0, 218.43459, 58.77853, 0, 1);
  }

  11% {
    z-index: 100.63742;
    transform: matrix3d(1.11247, 0, 0, 0, 0, 1.11247, 0, 0, 0, 0, 1, 0, 208.03858, 63.7424, 0, 1);
  }

  12% {
    z-index: 100.68455;
    transform: matrix3d(1.12818, 0, 0, 0, 0, 1.12818, 0, 0, 0, 0, 1, 0, 196.82153, 68.45471, 0, 1);
  }

  13% {
    z-index: 100.72897;
    transform: matrix3d(1.14299, 0, 0, 0, 0, 1.14299, 0, 0, 0, 0, 1, 0, 184.82772, 72.89686, 0, 1);
  }

  14% {
    z-index: 100.77051;
    transform: matrix3d(1.15684, 0, 0, 0, 0, 1.15684, 0, 0, 0, 0, 1, 0, 172.10448, 77.05132, 0, 1);
  }

  15% {
    z-index: 100.80902;
    transform: matrix3d(1.16967, 0, 0, 0, 0, 1.16967, 0, 0, 0, 0, 1, 0, 158.70202, 80.9017, 0, 1);
  }

  16% {
    z-index: 100.84433;
    transform: matrix3d(1.18144, 0, 0, 0, 0, 1.18144, 0, 0, 0, 0, 1, 0, 144.67323, 84.43279, 0, 1);
  }

  17% {
    z-index: 100.87631;
    transform: matrix3d(1.1921, 0, 0, 0, 0, 1.1921, 0, 0, 0, 0, 1, 0, 130.07349, 87.63067, 0, 1);
  }

  18% {
    z-index: 100.90483;
    transform: matrix3d(1.20161, 0, 0, 0, 0, 1.20161, 0, 0, 0, 0, 1, 0, 114.96041, 90.48271, 0, 1);
  }

  19% {
    z-index: 100.92978;
    transform: matrix3d(1.20993, 0, 0, 0, 0, 1.20993, 0, 0, 0, 0, 1, 0, 99.39363, 92.97765, 0, 1);
  }

  20% {
    z-index: 100.95106;
    transform: matrix3d(1.21702, 0, 0, 0, 0, 1.21702, 0, 0, 0, 0, 1, 0, 83.43459, 95.10565, 0, 1);
  }

  21% {
    z-index: 100.96858;
    transform: matrix3d(1.22286, 0, 0, 0, 0, 1.22286, 0, 0, 0, 0, 1, 0, 67.14627, 96.85832, 0, 1);
  }

  22% {
    z-index: 100.98229;
    transform: matrix3d(1.22743, 0, 0, 0, 0, 1.22743, 0, 0, 0, 0, 1, 0, 50.59295, 98.22873, 0, 1);
  }

  23% {
    z-index: 100.99211;
    transform: matrix3d(1.2307, 0, 0, 0, 0, 1.2307, 0, 0, 0, 0, 1, 0, 33.83997, 99.21147, 0, 1);
  }

  24% {
    z-index: 100.99803;
    transform: matrix3d(1.23268, 0, 0, 0, 0, 1.23268, 0, 0, 0, 0, 1, 0, 16.95344, 99.80267, 0, 1);
  }

  25% {
    z-index: 101;
    transform: matrix3d(1.23333, 0, 0, 0, 0, 1.23333, 0, 0, 0, 0, 1, 0, 0, 100, 0, 1);
  }

  26% {
    z-index: 100.99803;
    transform: matrix3d(1.23268, 0, 0, 0, 0, 1.23268, 0, 0, 0, 0, 1, 0, -16.95344, 99.80267, 0, 1);
  }

  27% {
    z-index: 100.99211;
    transform: matrix3d(1.2307, 0, 0, 0, 0, 1.2307, 0, 0, 0, 0, 1, 0, -33.83997, 99.21147, 0, 1);
  }

  28% {
    z-index: 100.98229;
    transform: matrix3d(1.22743, 0, 0, 0, 0, 1.22743, 0, 0, 0, 0, 1, 0, -50.59295, 98.22873, 0, 1);
  }

  29% {
    z-index: 100.96858;
    transform: matrix3d(1.22286, 0, 0, 0, 0, 1.22286, 0, 0, 0, 0, 1, 0, -67.14627, 96.85832, 0, 1);
  }

  30% {
    z-index: 100.95106;
    transform: matrix3d(1.21702, 0, 0, 0, 0, 1.21702, 0, 0, 0, 0, 1, 0, -83.43459, 95.10565, 0, 1);
  }

  31% {
    z-index: 100.92978;
    transform: matrix3d(1.20993, 0, 0, 0, 0, 1.20993, 0, 0, 0, 0, 1, 0, -99.39363, 92.97765, 0, 1);
  }

  32% {
    z-index: 100.90483;
    transform: matrix3d(1.20161, 0, 0, 0, 0, 1.20161, 0, 0, 0, 0, 1, 0, -114.96041, 90.48271, 0, 1);
  }

  33% {
    z-index: 100.87631;
    transform: matrix3d(1.1921, 0, 0, 0, 0, 1.1921, 0, 0, 0, 0, 1, 0, -130.07349, 87.63067, 0, 1);
  }

  34% {
    z-index: 100.84433;
    transform: matrix3d(1.18144, 0, 0, 0, 0, 1.18144, 0, 0, 0, 0, 1, 0, -144.67323, 84.43279, 0, 1);
  }

  35% {
    z-index: 100.80902;
    transform: matrix3d(1.16967, 0, 0, 0, 0, 1.16967, 0, 0, 0, 0, 1, 0, -158.70202, 80.9017, 0, 1);
  }

  36% {
    z-index: 100.77051;
    transform: matrix3d(1.15684, 0, 0, 0, 0, 1.15684, 0, 0, 0, 0, 1, 0, -172.10448, 77.05132, 0, 1);
  }

  37% {
    z-index: 100.72897;
    transform: matrix3d(1.14299, 0, 0, 0, 0, 1.14299, 0, 0, 0, 0, 1, 0, -184.82772, 72.89686, 0, 1);
  }

  38% {
    z-index: 100.68455;
    transform: matrix3d(1.12818, 0, 0, 0, 0, 1.12818, 0, 0, 0, 0, 1, 0, -196.82153, 68.45471, 0, 1);
  }

  39% {
    z-index: 100.63742;
    transform: matrix3d(1.11247, 0, 0, 0, 0, 1.11247, 0, 0, 0, 0, 1, 0, -208.03858, 63.7424, 0, 1);
  }

  40% {
    z-index: 100.58779;
    transform: matrix3d(1.09593, 0, 0, 0, 0, 1.09593, 0, 0, 0, 0, 1, 0, -218.43459, 58.77853, 0, 1);
  }

  41% {
    z-index: 100.53583;
    transform: matrix3d(1.07861, 0, 0, 0, 0, 1.07861, 0, 0, 0, 0, 1, 0, -227.96854, 53.58268, 0, 1);
  }

  42% {
    z-index: 100.48175;
    transform: matrix3d(1.06058, 0, 0, 0, 0, 1.06058, 0, 0, 0, 0, 1, 0, -236.6028, 48.17537, 0, 1);
  }

  43% {
    z-index: 100.42578;
    transform: matrix3d(1.04193, 0, 0, 0, 0, 1.04193, 0, 0, 0, 0, 1, 0, -244.3033, 42.57793, 0, 1);
  }

  44% {
    z-index: 100.36812;
    transform: matrix3d(1.02271, 0, 0, 0, 0, 1.02271, 0, 0, 0, 0, 1, 0, -251.03965, 36.81246, 0, 1);
  }

  45% {
    z-index: 100.30902;
    transform: matrix3d(1.00301, 0, 0, 0, 0, 1.00301, 0, 0, 0, 0, 1, 0, -256.78526, 30.9017, 0, 1);
  }

  46% {
    z-index: 100.24869;
    transform: matrix3d(0.9829, 0, 0, 0, 0, 0.9829, 0, 0, 0, 0, 1, 0, -261.51745, 24.86899, 0, 1);
  }

  47% {
    z-index: 100.18738;
    transform: matrix3d(0.96246, 0, 0, 0, 0, 0.96246, 0, 0, 0, 0, 1, 0, -265.21756, 18.73813, 0, 1);
  }

  48% {
    z-index: 100.12533;
    transform: matrix3d(0.94178, 0, 0, 0, 0, 0.94178, 0, 0, 0, 0, 1, 0, -267.87097, 12.53332, 0, 1);
  }

  49% {
    z-index: 100.06279;
    transform: matrix3d(0.92093, 0, 0, 0, 0, 0.92093, 0, 0, 0, 0, 1, 0, -269.46722, 6.27905, 0, 1);
  }

  50% {
    z-index: 100;
    transform: matrix3d(0.9, 0, 0, 0, 0, 0.9, 0, 0, 0, 0, 1, 0, -270, 0, 0, 1);
  }

  51% {
    z-index: 99.93721;
    transform: matrix3d(0.87907, 0, 0, 0, 0, 0.87907, 0, 0, 0, 0, 1, 0, -269.46722, -6.27905, 0, 1);
  }

  52% {
    z-index: 99.87467;
    transform: matrix3d(
      0.85822,
      0,
      0,
      0,
      0,
      0.85822,
      0,
      0,
      0,
      0,
      1,
      0,
      -267.87097,
      -12.53332,
      0,
      1
    );
  }

  53% {
    z-index: 99.81262;
    transform: matrix3d(
      0.83754,
      0,
      0,
      0,
      0,
      0.83754,
      0,
      0,
      0,
      0,
      1,
      0,
      -265.21756,
      -18.73813,
      0,
      1
    );
  }

  54% {
    z-index: 99.75131;
    transform: matrix3d(0.8171, 0, 0, 0, 0, 0.8171, 0, 0, 0, 0, 1, 0, -261.51745, -24.86899, 0, 1);
  }

  55% {
    z-index: 99.69098;
    transform: matrix3d(0.79699, 0, 0, 0, 0, 0.79699, 0, 0, 0, 0, 1, 0, -256.78526, -30.9017, 0, 1);
  }

  56% {
    z-index: 99.63188;
    transform: matrix3d(
      0.77729,
      0,
      0,
      0,
      0,
      0.77729,
      0,
      0,
      0,
      0,
      1,
      0,
      -251.03965,
      -36.81246,
      0,
      1
    );
  }

  57% {
    z-index: 99.57422;
    transform: matrix3d(0.75807, 0, 0, 0, 0, 0.75807, 0, 0, 0, 0, 1, 0, -244.3033, -42.57793, 0, 1);
  }

  58% {
    z-index: 99.51825;
    transform: matrix3d(0.73942, 0, 0, 0, 0, 0.73942, 0, 0, 0, 0, 1, 0, -236.6028, -48.17537, 0, 1);
  }

  59% {
    z-index: 99.46417;
    transform: matrix3d(
      0.72139,
      0,
      0,
      0,
      0,
      0.72139,
      0,
      0,
      0,
      0,
      1,
      0,
      -227.96854,
      -53.58268,
      0,
      1
    );
  }

  60% {
    z-index: 99.41221;
    transform: matrix3d(
      0.70407,
      0,
      0,
      0,
      0,
      0.70407,
      0,
      0,
      0,
      0,
      1,
      0,
      -218.43459,
      -58.77853,
      0,
      1
    );
  }

  61% {
    z-index: 99.36258;
    transform: matrix3d(0.68753, 0, 0, 0, 0, 0.68753, 0, 0, 0, 0, 1, 0, -208.03857, -63.7424, 0, 1);
  }

  62% {
    z-index: 99.31545;
    transform: matrix3d(
      0.67182,
      0,
      0,
      0,
      0,
      0.67182,
      0,
      0,
      0,
      0,
      1,
      0,
      -196.82153,
      -68.45471,
      0,
      1
    );
  }

  63% {
    z-index: 99.27103;
    transform: matrix3d(
      0.65701,
      0,
      0,
      0,
      0,
      0.65701,
      0,
      0,
      0,
      0,
      1,
      0,
      -184.82772,
      -72.89686,
      0,
      1
    );
  }

  64% {
    z-index: 99.22949;
    transform: matrix3d(
      0.64316,
      0,
      0,
      0,
      0,
      0.64316,
      0,
      0,
      0,
      0,
      1,
      0,
      -172.10447,
      -77.05132,
      0,
      1
    );
  }

  65% {
    z-index: 99.19098;
    transform: matrix3d(0.63033, 0, 0, 0, 0, 0.63033, 0, 0, 0, 0, 1, 0, -158.70201, -80.9017, 0, 1);
  }

  66% {
    z-index: 99.15567;
    transform: matrix3d(
      0.61856,
      0,
      0,
      0,
      0,
      0.61856,
      0,
      0,
      0,
      0,
      1,
      0,
      -144.67323,
      -84.43279,
      0,
      1
    );
  }

  67% {
    z-index: 99.12369;
    transform: matrix3d(0.6079, 0, 0, 0, 0, 0.6079, 0, 0, 0, 0, 1, 0, -130.07348, -87.63067, 0, 1);
  }

  68% {
    z-index: 99.09517;
    transform: matrix3d(0.59839, 0, 0, 0, 0, 0.59839, 0, 0, 0, 0, 1, 0, -114.96039, -90.4827, 0, 1);
  }

  69% {
    z-index: 99.07022;
    transform: matrix3d(0.59007, 0, 0, 0, 0, 0.59007, 0, 0, 0, 0, 1, 0, -99.39361, -92.97765, 0, 1);
  }

  70% {
    z-index: 99.04894;
    transform: matrix3d(0.58298, 0, 0, 0, 0, 0.58298, 0, 0, 0, 0, 1, 0, -83.43456, -95.10565, 0, 1);
  }

  71% {
    z-index: 99.03142;
    transform: matrix3d(0.57714, 0, 0, 0, 0, 0.57714, 0, 0, 0, 0, 1, 0, -67.14622, -96.85831, 0, 1);
  }

  72% {
    z-index: 99.01771;
    transform: matrix3d(0.57257, 0, 0, 0, 0, 0.57257, 0, 0, 0, 0, 1, 0, -50.59289, -98.22872, 0, 1);
  }

  73% {
    z-index: 99.00789;
    transform: matrix3d(0.5693, 0, 0, 0, 0, 0.5693, 0, 0, 0, 0, 1, 0, -33.83989, -99.21146, 0, 1);
  }

  74% {
    z-index: 99.00197;
    transform: matrix3d(0.56732, 0, 0, 0, 0, 0.56732, 0, 0, 0, 0, 1, 0, -16.95333, -99.80266, 0, 1);
  }

  75% {
    z-index: 99;
    transform: matrix3d(0.56667, 0, 0, 0, 0, 0.56667, 0, 0, 0, 0, 1, 0, 0.00015, -99.99999, 0, 1);
  }

  76% {
    z-index: 99.00197;
    transform: matrix3d(0.56732, 0, 0, 0, 0, 0.56732, 0, 0, 0, 0, 1, 0, 16.95364, -99.80266, 0, 1);
  }

  77% {
    z-index: 99.00789;
    transform: matrix3d(0.5693, 0, 0, 0, 0, 0.5693, 0, 0, 0, 0, 1, 0, 33.84024, -99.21145, 0, 1);
  }

  78% {
    z-index: 99.01771;
    transform: matrix3d(0.57257, 0, 0, 0, 0, 0.57257, 0, 0, 0, 0, 1, 0, 50.59331, -98.2287, 0, 1);
  }

  79% {
    z-index: 99.03142;
    transform: matrix3d(0.57714, 0, 0, 0, 0, 0.57714, 0, 0, 0, 0, 1, 0, 67.14674, -96.85828, 0, 1);
  }

  80% {
    z-index: 99.04894;
    transform: matrix3d(0.58298, 0, 0, 0, 0, 0.58298, 0, 0, 0, 0, 1, 0, 83.4352, -95.1056, 0, 1);
  }

  81% {
    z-index: 99.07022;
    transform: matrix3d(0.59007, 0, 0, 0, 0, 0.59007, 0, 0, 0, 0, 1, 0, 99.39444, -92.97758, 0, 1);
  }

  82% {
    z-index: 99.09517;
    transform: matrix3d(0.59839, 0, 0, 0, 0, 0.59839, 0, 0, 0, 0, 1, 0, 114.96147, -90.48262, 0, 1);
  }

  83% {
    z-index: 99.12369;
    transform: matrix3d(0.6079, 0, 0, 0, 0, 0.6079, 0, 0, 0, 0, 1, 0, 130.07487, -87.63055, 0, 1);
  }

  84% {
    z-index: 99.15567;
    transform: matrix3d(0.61856, 0, 0, 0, 0, 0.61856, 0, 0, 0, 0, 1, 0, 144.67503, -84.43264, 0, 1);
  }

  85% {
    z-index: 99.19099;
    transform: matrix3d(0.63033, 0, 0, 0, 0, 0.63033, 0, 0, 0, 0, 1, 0, 158.70434, -80.9015, 0, 1);
  }

  86% {
    z-index: 99.22949;
    transform: matrix3d(0.64316, 0, 0, 0, 0, 0.64316, 0, 0, 0, 0, 1, 0, 172.10748, -77.05106, 0, 1);
  }

  87% {
    z-index: 99.27103;
    transform: matrix3d(0.65701, 0, 0, 0, 0, 0.65701, 0, 0, 0, 0, 1, 0, 184.83158, -72.89652, 0, 1);
  }

  88% {
    z-index: 99.31546;
    transform: matrix3d(0.67182, 0, 0, 0, 0, 0.67182, 0, 0, 0, 0, 1, 0, 196.82649, -68.45427, 0, 1);
  }

  89% {
    z-index: 99.36258;
    transform: matrix3d(0.68753, 0, 0, 0, 0, 0.68753, 0, 0, 0, 0, 1, 0, 208.04493, -63.74182, 0, 1);
  }

  90% {
    z-index: 99.41222;
    transform: matrix3d(0.70407, 0, 0, 0, 0, 0.70407, 0, 0, 0, 0, 1, 0, 218.4427, -58.77778, 0, 1);
  }

  91% {
    z-index: 99.46418;
    transform: matrix3d(0.72139, 0, 0, 0, 0, 0.72139, 0, 0, 0, 0, 1, 0, 227.97887, -53.58172, 0, 1);
  }

  92% {
    z-index: 99.51826;
    transform: matrix3d(0.73942, 0, 0, 0, 0, 0.73942, 0, 0, 0, 0, 1, 0, 236.61593, -48.17414, 0, 1);
  }

  93% {
    z-index: 99.57424;
    transform: matrix3d(0.75808, 0, 0, 0, 0, 0.75808, 0, 0, 0, 0, 1, 0, 244.31993, -42.57636, 0, 1);
  }

  94% {
    z-index: 99.6319;
    transform: matrix3d(0.7773, 0, 0, 0, 0, 0.7773, 0, 0, 0, 0, 1, 0, 251.06067, -36.81045, 0, 1);
  }

  95% {
    z-index: 99.69101;
    transform: matrix3d(0.797, 0, 0, 0, 0, 0.797, 0, 0, 0, 0, 1, 0, 256.81175, -30.89914, 0, 1);
  }

  96% {
    z-index: 99.75134;
    transform: matrix3d(0.81711, 0, 0, 0, 0, 0.81711, 0, 0, 0, 0, 1, 0, 261.55076, -24.86574, 0, 1);
  }

  97% {
    z-index: 99.81266;
    transform: matrix3d(0.83755, 0, 0, 0, 0, 0.83755, 0, 0, 0, 0, 1, 0, 265.25934, -18.73401, 0, 1);
  }

  98% {
    z-index: 99.87472;
    transform: matrix3d(0.85824, 0, 0, 0, 0, 0.85824, 0, 0, 0, 0, 1, 0, 267.92326, -12.52811, 0, 1);
  }

  99% {
    z-index: 99.93728;
    transform: matrix3d(0.87909, 0, 0, 0, 0, 0.87909, 0, 0, 0, 0, 1, 0, 269.5325, -6.27248, 0, 1);
  }

  100% {
    z-index: 100.00008;
    transform: matrix3d(0.90003, 0, 0, 0, 0, 0.90003, 0, 0, 0, 0, 1, 0, 270.08133, 0.00827, 0, 1);
  }
}

@keyframes rotate6 {
  0% {
    z-index: 100.99803;
    transform: matrix3d(1.23268, 0, 0, 0, 0, 1.23268, 0, 0, 0, 0, 1, 0, -16.95344, 99.80267, 0, 1);
  }

  1% {
    z-index: 100.99211;
    transform: matrix3d(1.2307, 0, 0, 0, 0, 1.2307, 0, 0, 0, 0, 1, 0, -33.83997, 99.21147, 0, 1);
  }

  2% {
    z-index: 100.98229;
    transform: matrix3d(1.22743, 0, 0, 0, 0, 1.22743, 0, 0, 0, 0, 1, 0, -50.59295, 98.22873, 0, 1);
  }

  3% {
    z-index: 100.96858;
    transform: matrix3d(1.22286, 0, 0, 0, 0, 1.22286, 0, 0, 0, 0, 1, 0, -67.14627, 96.85832, 0, 1);
  }

  4% {
    z-index: 100.95106;
    transform: matrix3d(1.21702, 0, 0, 0, 0, 1.21702, 0, 0, 0, 0, 1, 0, -83.43459, 95.10565, 0, 1);
  }

  5% {
    z-index: 100.92978;
    transform: matrix3d(1.20993, 0, 0, 0, 0, 1.20993, 0, 0, 0, 0, 1, 0, -99.39363, 92.97765, 0, 1);
  }

  6% {
    z-index: 100.90483;
    transform: matrix3d(1.20161, 0, 0, 0, 0, 1.20161, 0, 0, 0, 0, 1, 0, -114.96041, 90.48271, 0, 1);
  }

  7% {
    z-index: 100.87631;
    transform: matrix3d(1.1921, 0, 0, 0, 0, 1.1921, 0, 0, 0, 0, 1, 0, -130.07349, 87.63067, 0, 1);
  }

  8% {
    z-index: 100.84433;
    transform: matrix3d(1.18144, 0, 0, 0, 0, 1.18144, 0, 0, 0, 0, 1, 0, -144.67323, 84.43279, 0, 1);
  }

  9% {
    z-index: 100.80902;
    transform: matrix3d(1.16967, 0, 0, 0, 0, 1.16967, 0, 0, 0, 0, 1, 0, -158.70202, 80.9017, 0, 1);
  }

  10% {
    z-index: 100.77051;
    transform: matrix3d(1.15684, 0, 0, 0, 0, 1.15684, 0, 0, 0, 0, 1, 0, -172.10448, 77.05132, 0, 1);
  }

  11% {
    z-index: 100.72897;
    transform: matrix3d(1.14299, 0, 0, 0, 0, 1.14299, 0, 0, 0, 0, 1, 0, -184.82772, 72.89686, 0, 1);
  }

  12% {
    z-index: 100.68455;
    transform: matrix3d(1.12818, 0, 0, 0, 0, 1.12818, 0, 0, 0, 0, 1, 0, -196.82153, 68.45471, 0, 1);
  }

  13% {
    z-index: 100.63742;
    transform: matrix3d(1.11247, 0, 0, 0, 0, 1.11247, 0, 0, 0, 0, 1, 0, -208.03858, 63.7424, 0, 1);
  }

  14% {
    z-index: 100.58779;
    transform: matrix3d(1.09593, 0, 0, 0, 0, 1.09593, 0, 0, 0, 0, 1, 0, -218.43459, 58.77853, 0, 1);
  }

  15% {
    z-index: 100.53583;
    transform: matrix3d(1.07861, 0, 0, 0, 0, 1.07861, 0, 0, 0, 0, 1, 0, -227.96854, 53.58268, 0, 1);
  }

  16% {
    z-index: 100.48175;
    transform: matrix3d(1.06058, 0, 0, 0, 0, 1.06058, 0, 0, 0, 0, 1, 0, -236.6028, 48.17537, 0, 1);
  }

  17% {
    z-index: 100.42578;
    transform: matrix3d(1.04193, 0, 0, 0, 0, 1.04193, 0, 0, 0, 0, 1, 0, -244.3033, 42.57793, 0, 1);
  }

  18% {
    z-index: 100.36812;
    transform: matrix3d(1.02271, 0, 0, 0, 0, 1.02271, 0, 0, 0, 0, 1, 0, -251.03965, 36.81246, 0, 1);
  }

  19% {
    z-index: 100.30902;
    transform: matrix3d(1.00301, 0, 0, 0, 0, 1.00301, 0, 0, 0, 0, 1, 0, -256.78526, 30.9017, 0, 1);
  }

  20% {
    z-index: 100.24869;
    transform: matrix3d(0.9829, 0, 0, 0, 0, 0.9829, 0, 0, 0, 0, 1, 0, -261.51745, 24.86899, 0, 1);
  }

  21% {
    z-index: 100.18738;
    transform: matrix3d(0.96246, 0, 0, 0, 0, 0.96246, 0, 0, 0, 0, 1, 0, -265.21756, 18.73813, 0, 1);
  }

  22% {
    z-index: 100.12533;
    transform: matrix3d(0.94178, 0, 0, 0, 0, 0.94178, 0, 0, 0, 0, 1, 0, -267.87097, 12.53332, 0, 1);
  }

  23% {
    z-index: 100.06279;
    transform: matrix3d(0.92093, 0, 0, 0, 0, 0.92093, 0, 0, 0, 0, 1, 0, -269.46722, 6.27905, 0, 1);
  }

  24% {
    z-index: 100;
    transform: matrix3d(0.9, 0, 0, 0, 0, 0.9, 0, 0, 0, 0, 1, 0, -270, 0, 0, 1);
  }

  25% {
    z-index: 99.93721;
    transform: matrix3d(0.87907, 0, 0, 0, 0, 0.87907, 0, 0, 0, 0, 1, 0, -269.46722, -6.27905, 0, 1);
  }

  26% {
    z-index: 99.87467;
    transform: matrix3d(
      0.85822,
      0,
      0,
      0,
      0,
      0.85822,
      0,
      0,
      0,
      0,
      1,
      0,
      -267.87097,
      -12.53332,
      0,
      1
    );
  }

  27% {
    z-index: 99.81262;
    transform: matrix3d(
      0.83754,
      0,
      0,
      0,
      0,
      0.83754,
      0,
      0,
      0,
      0,
      1,
      0,
      -265.21756,
      -18.73813,
      0,
      1
    );
  }

  28% {
    z-index: 99.75131;
    transform: matrix3d(0.8171, 0, 0, 0, 0, 0.8171, 0, 0, 0, 0, 1, 0, -261.51745, -24.86899, 0, 1);
  }

  29% {
    z-index: 99.69098;
    transform: matrix3d(0.79699, 0, 0, 0, 0, 0.79699, 0, 0, 0, 0, 1, 0, -256.78526, -30.9017, 0, 1);
  }

  30% {
    z-index: 99.63188;
    transform: matrix3d(
      0.77729,
      0,
      0,
      0,
      0,
      0.77729,
      0,
      0,
      0,
      0,
      1,
      0,
      -251.03965,
      -36.81246,
      0,
      1
    );
  }

  31% {
    z-index: 99.57422;
    transform: matrix3d(0.75807, 0, 0, 0, 0, 0.75807, 0, 0, 0, 0, 1, 0, -244.3033, -42.57793, 0, 1);
  }

  32% {
    z-index: 99.51825;
    transform: matrix3d(0.73942, 0, 0, 0, 0, 0.73942, 0, 0, 0, 0, 1, 0, -236.6028, -48.17537, 0, 1);
  }

  33% {
    z-index: 99.46417;
    transform: matrix3d(
      0.72139,
      0,
      0,
      0,
      0,
      0.72139,
      0,
      0,
      0,
      0,
      1,
      0,
      -227.96854,
      -53.58268,
      0,
      1
    );
  }

  34% {
    z-index: 99.41221;
    transform: matrix3d(
      0.70407,
      0,
      0,
      0,
      0,
      0.70407,
      0,
      0,
      0,
      0,
      1,
      0,
      -218.43459,
      -58.77853,
      0,
      1
    );
  }

  35% {
    z-index: 99.36258;
    transform: matrix3d(0.68753, 0, 0, 0, 0, 0.68753, 0, 0, 0, 0, 1, 0, -208.03857, -63.7424, 0, 1);
  }

  36% {
    z-index: 99.31545;
    transform: matrix3d(
      0.67182,
      0,
      0,
      0,
      0,
      0.67182,
      0,
      0,
      0,
      0,
      1,
      0,
      -196.82153,
      -68.45471,
      0,
      1
    );
  }

  37% {
    z-index: 99.27103;
    transform: matrix3d(
      0.65701,
      0,
      0,
      0,
      0,
      0.65701,
      0,
      0,
      0,
      0,
      1,
      0,
      -184.82772,
      -72.89686,
      0,
      1
    );
  }

  38% {
    z-index: 99.22949;
    transform: matrix3d(
      0.64316,
      0,
      0,
      0,
      0,
      0.64316,
      0,
      0,
      0,
      0,
      1,
      0,
      -172.10447,
      -77.05132,
      0,
      1
    );
  }

  39% {
    z-index: 99.19098;
    transform: matrix3d(0.63033, 0, 0, 0, 0, 0.63033, 0, 0, 0, 0, 1, 0, -158.70201, -80.9017, 0, 1);
  }

  40% {
    z-index: 99.15567;
    transform: matrix3d(
      0.61856,
      0,
      0,
      0,
      0,
      0.61856,
      0,
      0,
      0,
      0,
      1,
      0,
      -144.67323,
      -84.43279,
      0,
      1
    );
  }

  41% {
    z-index: 99.12369;
    transform: matrix3d(0.6079, 0, 0, 0, 0, 0.6079, 0, 0, 0, 0, 1, 0, -130.07348, -87.63067, 0, 1);
  }

  42% {
    z-index: 99.09517;
    transform: matrix3d(0.59839, 0, 0, 0, 0, 0.59839, 0, 0, 0, 0, 1, 0, -114.96039, -90.4827, 0, 1);
  }

  43% {
    z-index: 99.07022;
    transform: matrix3d(0.59007, 0, 0, 0, 0, 0.59007, 0, 0, 0, 0, 1, 0, -99.39361, -92.97765, 0, 1);
  }

  44% {
    z-index: 99.04894;
    transform: matrix3d(0.58298, 0, 0, 0, 0, 0.58298, 0, 0, 0, 0, 1, 0, -83.43456, -95.10565, 0, 1);
  }

  45% {
    z-index: 99.03142;
    transform: matrix3d(0.57714, 0, 0, 0, 0, 0.57714, 0, 0, 0, 0, 1, 0, -67.14622, -96.85831, 0, 1);
  }

  46% {
    z-index: 99.01771;
    transform: matrix3d(0.57257, 0, 0, 0, 0, 0.57257, 0, 0, 0, 0, 1, 0, -50.59289, -98.22872, 0, 1);
  }

  47% {
    z-index: 99.00789;
    transform: matrix3d(0.5693, 0, 0, 0, 0, 0.5693, 0, 0, 0, 0, 1, 0, -33.83989, -99.21146, 0, 1);
  }

  48% {
    z-index: 99.00197;
    transform: matrix3d(0.56732, 0, 0, 0, 0, 0.56732, 0, 0, 0, 0, 1, 0, -16.95333, -99.80266, 0, 1);
  }

  49% {
    z-index: 99;
    transform: matrix3d(0.56667, 0, 0, 0, 0, 0.56667, 0, 0, 0, 0, 1, 0, 0.00015, -99.99999, 0, 1);
  }

  50% {
    z-index: 99.00197;
    transform: matrix3d(0.56732, 0, 0, 0, 0, 0.56732, 0, 0, 0, 0, 1, 0, 16.95364, -99.80266, 0, 1);
  }

  51% {
    z-index: 99.00789;
    transform: matrix3d(0.5693, 0, 0, 0, 0, 0.5693, 0, 0, 0, 0, 1, 0, 33.84024, -99.21145, 0, 1);
  }

  52% {
    z-index: 99.01771;
    transform: matrix3d(0.57257, 0, 0, 0, 0, 0.57257, 0, 0, 0, 0, 1, 0, 50.59331, -98.2287, 0, 1);
  }

  53% {
    z-index: 99.03142;
    transform: matrix3d(0.57714, 0, 0, 0, 0, 0.57714, 0, 0, 0, 0, 1, 0, 67.14674, -96.85828, 0, 1);
  }

  54% {
    z-index: 99.04894;
    transform: matrix3d(0.58298, 0, 0, 0, 0, 0.58298, 0, 0, 0, 0, 1, 0, 83.4352, -95.1056, 0, 1);
  }

  55% {
    z-index: 99.07022;
    transform: matrix3d(0.59007, 0, 0, 0, 0, 0.59007, 0, 0, 0, 0, 1, 0, 99.39444, -92.97758, 0, 1);
  }

  56% {
    z-index: 99.09517;
    transform: matrix3d(0.59839, 0, 0, 0, 0, 0.59839, 0, 0, 0, 0, 1, 0, 114.96147, -90.48262, 0, 1);
  }

  57% {
    z-index: 99.12369;
    transform: matrix3d(0.6079, 0, 0, 0, 0, 0.6079, 0, 0, 0, 0, 1, 0, 130.07487, -87.63055, 0, 1);
  }

  58% {
    z-index: 99.15567;
    transform: matrix3d(0.61856, 0, 0, 0, 0, 0.61856, 0, 0, 0, 0, 1, 0, 144.67503, -84.43264, 0, 1);
  }

  59% {
    z-index: 99.19099;
    transform: matrix3d(0.63033, 0, 0, 0, 0, 0.63033, 0, 0, 0, 0, 1, 0, 158.70434, -80.9015, 0, 1);
  }

  60% {
    z-index: 99.22949;
    transform: matrix3d(0.64316, 0, 0, 0, 0, 0.64316, 0, 0, 0, 0, 1, 0, 172.10748, -77.05106, 0, 1);
  }

  61% {
    z-index: 99.27103;
    transform: matrix3d(0.65701, 0, 0, 0, 0, 0.65701, 0, 0, 0, 0, 1, 0, 184.83158, -72.89652, 0, 1);
  }

  62% {
    z-index: 99.31546;
    transform: matrix3d(0.67182, 0, 0, 0, 0, 0.67182, 0, 0, 0, 0, 1, 0, 196.82649, -68.45427, 0, 1);
  }

  63% {
    z-index: 99.36258;
    transform: matrix3d(0.68753, 0, 0, 0, 0, 0.68753, 0, 0, 0, 0, 1, 0, 208.04493, -63.74182, 0, 1);
  }

  64% {
    z-index: 99.41222;
    transform: matrix3d(0.70407, 0, 0, 0, 0, 0.70407, 0, 0, 0, 0, 1, 0, 218.4427, -58.77778, 0, 1);
  }

  65% {
    z-index: 99.46418;
    transform: matrix3d(0.72139, 0, 0, 0, 0, 0.72139, 0, 0, 0, 0, 1, 0, 227.97887, -53.58172, 0, 1);
  }

  66% {
    z-index: 99.51826;
    transform: matrix3d(0.73942, 0, 0, 0, 0, 0.73942, 0, 0, 0, 0, 1, 0, 236.61593, -48.17414, 0, 1);
  }

  67% {
    z-index: 99.57424;
    transform: matrix3d(0.75808, 0, 0, 0, 0, 0.75808, 0, 0, 0, 0, 1, 0, 244.31993, -42.57636, 0, 1);
  }

  68% {
    z-index: 99.6319;
    transform: matrix3d(0.7773, 0, 0, 0, 0, 0.7773, 0, 0, 0, 0, 1, 0, 251.06067, -36.81045, 0, 1);
  }

  69% {
    z-index: 99.69101;
    transform: matrix3d(0.797, 0, 0, 0, 0, 0.797, 0, 0, 0, 0, 1, 0, 256.81175, -30.89914, 0, 1);
  }

  70% {
    z-index: 99.75134;
    transform: matrix3d(0.81711, 0, 0, 0, 0, 0.81711, 0, 0, 0, 0, 1, 0, 261.55076, -24.86574, 0, 1);
  }

  71% {
    z-index: 99.81266;
    transform: matrix3d(0.83755, 0, 0, 0, 0, 0.83755, 0, 0, 0, 0, 1, 0, 265.25934, -18.73401, 0, 1);
  }

  72% {
    z-index: 99.87472;
    transform: matrix3d(0.85824, 0, 0, 0, 0, 0.85824, 0, 0, 0, 0, 1, 0, 267.92326, -12.52811, 0, 1);
  }

  73% {
    z-index: 99.93728;
    transform: matrix3d(0.87909, 0, 0, 0, 0, 0.87909, 0, 0, 0, 0, 1, 0, 269.5325, -6.27248, 0, 1);
  }

  74% {
    z-index: 100.00008;
    transform: matrix3d(0.90003, 0, 0, 0, 0, 0.90003, 0, 0, 0, 0, 1, 0, 270.08133, 0.00827, 0, 1);
  }

  75% {
    z-index: 100;
    transform: matrix3d(0.9, 0, 0, 0, 0, 0.9, 0, 0, 0, 0, 1, 0, 270, 0, 0, 1);
  }

  76% {
    z-index: 100.06279;
    transform: matrix3d(0.92093, 0, 0, 0, 0, 0.92093, 0, 0, 0, 0, 1, 0, 269.46722, 6.27905, 0, 1);
  }

  77% {
    z-index: 100.12533;
    transform: matrix3d(0.94178, 0, 0, 0, 0, 0.94178, 0, 0, 0, 0, 1, 0, 267.87097, 12.53332, 0, 1);
  }

  78% {
    z-index: 100.18738;
    transform: matrix3d(0.96246, 0, 0, 0, 0, 0.96246, 0, 0, 0, 0, 1, 0, 265.21756, 18.73813, 0, 1);
  }

  79% {
    z-index: 100.24869;
    transform: matrix3d(0.9829, 0, 0, 0, 0, 0.9829, 0, 0, 0, 0, 1, 0, 261.51745, 24.86899, 0, 1);
  }

  80% {
    z-index: 100.30902;
    transform: matrix3d(1.00301, 0, 0, 0, 0, 1.00301, 0, 0, 0, 0, 1, 0, 256.78526, 30.9017, 0, 1);
  }

  81% {
    z-index: 100.36812;
    transform: matrix3d(1.02271, 0, 0, 0, 0, 1.02271, 0, 0, 0, 0, 1, 0, 251.03965, 36.81246, 0, 1);
  }

  82% {
    z-index: 100.42578;
    transform: matrix3d(1.04193, 0, 0, 0, 0, 1.04193, 0, 0, 0, 0, 1, 0, 244.3033, 42.57793, 0, 1);
  }

  83% {
    z-index: 100.48175;
    transform: matrix3d(1.06058, 0, 0, 0, 0, 1.06058, 0, 0, 0, 0, 1, 0, 236.6028, 48.17537, 0, 1);
  }

  84% {
    z-index: 100.53583;
    transform: matrix3d(1.07861, 0, 0, 0, 0, 1.07861, 0, 0, 0, 0, 1, 0, 227.96854, 53.58268, 0, 1);
  }

  85% {
    z-index: 100.58779;
    transform: matrix3d(1.09593, 0, 0, 0, 0, 1.09593, 0, 0, 0, 0, 1, 0, 218.43459, 58.77853, 0, 1);
  }

  86% {
    z-index: 100.63742;
    transform: matrix3d(1.11247, 0, 0, 0, 0, 1.11247, 0, 0, 0, 0, 1, 0, 208.03858, 63.7424, 0, 1);
  }

  87% {
    z-index: 100.68455;
    transform: matrix3d(1.12818, 0, 0, 0, 0, 1.12818, 0, 0, 0, 0, 1, 0, 196.82153, 68.45471, 0, 1);
  }

  88% {
    z-index: 100.72897;
    transform: matrix3d(1.14299, 0, 0, 0, 0, 1.14299, 0, 0, 0, 0, 1, 0, 184.82772, 72.89686, 0, 1);
  }

  89% {
    z-index: 100.77051;
    transform: matrix3d(1.15684, 0, 0, 0, 0, 1.15684, 0, 0, 0, 0, 1, 0, 172.10448, 77.05132, 0, 1);
  }

  90% {
    z-index: 100.80902;
    transform: matrix3d(1.16967, 0, 0, 0, 0, 1.16967, 0, 0, 0, 0, 1, 0, 158.70202, 80.9017, 0, 1);
  }

  91% {
    z-index: 100.84433;
    transform: matrix3d(1.18144, 0, 0, 0, 0, 1.18144, 0, 0, 0, 0, 1, 0, 144.67323, 84.43279, 0, 1);
  }

  92% {
    z-index: 100.87631;
    transform: matrix3d(1.1921, 0, 0, 0, 0, 1.1921, 0, 0, 0, 0, 1, 0, 130.07349, 87.63067, 0, 1);
  }

  93% {
    z-index: 100.90483;
    transform: matrix3d(1.20161, 0, 0, 0, 0, 1.20161, 0, 0, 0, 0, 1, 0, 114.96041, 90.48271, 0, 1);
  }

  94% {
    z-index: 100.92978;
    transform: matrix3d(1.20993, 0, 0, 0, 0, 1.20993, 0, 0, 0, 0, 1, 0, 99.39363, 92.97765, 0, 1);
  }

  95% {
    z-index: 100.95106;
    transform: matrix3d(1.21702, 0, 0, 0, 0, 1.21702, 0, 0, 0, 0, 1, 0, 83.43459, 95.10565, 0, 1);
  }

  96% {
    z-index: 100.96858;
    transform: matrix3d(1.22286, 0, 0, 0, 0, 1.22286, 0, 0, 0, 0, 1, 0, 67.14627, 96.85832, 0, 1);
  }

  97% {
    z-index: 100.98229;
    transform: matrix3d(1.22743, 0, 0, 0, 0, 1.22743, 0, 0, 0, 0, 1, 0, 50.59295, 98.22873, 0, 1);
  }

  98% {
    z-index: 100.99211;
    transform: matrix3d(1.2307, 0, 0, 0, 0, 1.2307, 0, 0, 0, 0, 1, 0, 33.83997, 99.21147, 0, 1);
  }

  99% {
    z-index: 100.99803;
    transform: matrix3d(1.23268, 0, 0, 0, 0, 1.23268, 0, 0, 0, 0, 1, 0, 16.95344, 99.80267, 0, 1);
  }

  100% {
    z-index: 101;
    transform: matrix3d(1.23333, 0, 0, 0, 0, 1.23333, 0, 0, 0, 0, 1, 0, 0, 100, 0, 1);
  }
}

@keyframes rotate7 {
  0% {
    z-index: 99.87467;
    transform: matrix3d(
      0.85822,
      0,
      0,
      0,
      0,
      0.85822,
      0,
      0,
      0,
      0,
      1,
      0,
      -267.87097,
      -12.53332,
      0,
      1
    );
  }

  1% {
    z-index: 99.81262;
    transform: matrix3d(
      0.83754,
      0,
      0,
      0,
      0,
      0.83754,
      0,
      0,
      0,
      0,
      1,
      0,
      -265.21756,
      -18.73813,
      0,
      1
    );
  }

  2% {
    z-index: 99.75131;
    transform: matrix3d(0.8171, 0, 0, 0, 0, 0.8171, 0, 0, 0, 0, 1, 0, -261.51745, -24.86899, 0, 1);
  }

  3% {
    z-index: 99.69098;
    transform: matrix3d(0.79699, 0, 0, 0, 0, 0.79699, 0, 0, 0, 0, 1, 0, -256.78526, -30.9017, 0, 1);
  }

  4% {
    z-index: 99.63188;
    transform: matrix3d(
      0.77729,
      0,
      0,
      0,
      0,
      0.77729,
      0,
      0,
      0,
      0,
      1,
      0,
      -251.03965,
      -36.81246,
      0,
      1
    );
  }

  5% {
    z-index: 99.57422;
    transform: matrix3d(0.75807, 0, 0, 0, 0, 0.75807, 0, 0, 0, 0, 1, 0, -244.3033, -42.57793, 0, 1);
  }

  6% {
    z-index: 99.51825;
    transform: matrix3d(0.73942, 0, 0, 0, 0, 0.73942, 0, 0, 0, 0, 1, 0, -236.6028, -48.17537, 0, 1);
  }

  7% {
    z-index: 99.46417;
    transform: matrix3d(
      0.72139,
      0,
      0,
      0,
      0,
      0.72139,
      0,
      0,
      0,
      0,
      1,
      0,
      -227.96854,
      -53.58268,
      0,
      1
    );
  }

  8% {
    z-index: 99.41221;
    transform: matrix3d(
      0.70407,
      0,
      0,
      0,
      0,
      0.70407,
      0,
      0,
      0,
      0,
      1,
      0,
      -218.43459,
      -58.77853,
      0,
      1
    );
  }

  9% {
    z-index: 99.36258;
    transform: matrix3d(0.68753, 0, 0, 0, 0, 0.68753, 0, 0, 0, 0, 1, 0, -208.03857, -63.7424, 0, 1);
  }

  10% {
    z-index: 99.31545;
    transform: matrix3d(
      0.67182,
      0,
      0,
      0,
      0,
      0.67182,
      0,
      0,
      0,
      0,
      1,
      0,
      -196.82153,
      -68.45471,
      0,
      1
    );
  }

  11% {
    z-index: 99.27103;
    transform: matrix3d(
      0.65701,
      0,
      0,
      0,
      0,
      0.65701,
      0,
      0,
      0,
      0,
      1,
      0,
      -184.82772,
      -72.89686,
      0,
      1
    );
  }

  12% {
    z-index: 99.22949;
    transform: matrix3d(
      0.64316,
      0,
      0,
      0,
      0,
      0.64316,
      0,
      0,
      0,
      0,
      1,
      0,
      -172.10447,
      -77.05132,
      0,
      1
    );
  }

  13% {
    z-index: 99.19098;
    transform: matrix3d(0.63033, 0, 0, 0, 0, 0.63033, 0, 0, 0, 0, 1, 0, -158.70201, -80.9017, 0, 1);
  }

  14% {
    z-index: 99.15567;
    transform: matrix3d(
      0.61856,
      0,
      0,
      0,
      0,
      0.61856,
      0,
      0,
      0,
      0,
      1,
      0,
      -144.67323,
      -84.43279,
      0,
      1
    );
  }

  15% {
    z-index: 99.12369;
    transform: matrix3d(0.6079, 0, 0, 0, 0, 0.6079, 0, 0, 0, 0, 1, 0, -130.07348, -87.63067, 0, 1);
  }

  16% {
    z-index: 99.09517;
    transform: matrix3d(0.59839, 0, 0, 0, 0, 0.59839, 0, 0, 0, 0, 1, 0, -114.96039, -90.4827, 0, 1);
  }

  17% {
    z-index: 99.07022;
    transform: matrix3d(0.59007, 0, 0, 0, 0, 0.59007, 0, 0, 0, 0, 1, 0, -99.39361, -92.97765, 0, 1);
  }

  18% {
    z-index: 99.04894;
    transform: matrix3d(0.58298, 0, 0, 0, 0, 0.58298, 0, 0, 0, 0, 1, 0, -83.43456, -95.10565, 0, 1);
  }

  19% {
    z-index: 99.03142;
    transform: matrix3d(0.57714, 0, 0, 0, 0, 0.57714, 0, 0, 0, 0, 1, 0, -67.14622, -96.85831, 0, 1);
  }

  20% {
    z-index: 99.01771;
    transform: matrix3d(0.57257, 0, 0, 0, 0, 0.57257, 0, 0, 0, 0, 1, 0, -50.59289, -98.22872, 0, 1);
  }

  21% {
    z-index: 99.00789;
    transform: matrix3d(0.5693, 0, 0, 0, 0, 0.5693, 0, 0, 0, 0, 1, 0, -33.83989, -99.21146, 0, 1);
  }

  22% {
    z-index: 99.00197;
    transform: matrix3d(0.56732, 0, 0, 0, 0, 0.56732, 0, 0, 0, 0, 1, 0, -16.95333, -99.80266, 0, 1);
  }

  23% {
    z-index: 99;
    transform: matrix3d(0.56667, 0, 0, 0, 0, 0.56667, 0, 0, 0, 0, 1, 0, 0.00015, -99.99999, 0, 1);
  }

  24% {
    z-index: 99.00197;
    transform: matrix3d(0.56732, 0, 0, 0, 0, 0.56732, 0, 0, 0, 0, 1, 0, 16.95364, -99.80266, 0, 1);
  }

  25% {
    z-index: 99.00789;
    transform: matrix3d(0.5693, 0, 0, 0, 0, 0.5693, 0, 0, 0, 0, 1, 0, 33.84024, -99.21145, 0, 1);
  }

  26% {
    z-index: 99.01771;
    transform: matrix3d(0.57257, 0, 0, 0, 0, 0.57257, 0, 0, 0, 0, 1, 0, 50.59331, -98.2287, 0, 1);
  }

  27% {
    z-index: 99.03142;
    transform: matrix3d(0.57714, 0, 0, 0, 0, 0.57714, 0, 0, 0, 0, 1, 0, 67.14674, -96.85828, 0, 1);
  }

  28% {
    z-index: 99.04894;
    transform: matrix3d(0.58298, 0, 0, 0, 0, 0.58298, 0, 0, 0, 0, 1, 0, 83.4352, -95.1056, 0, 1);
  }

  29% {
    z-index: 99.07022;
    transform: matrix3d(0.59007, 0, 0, 0, 0, 0.59007, 0, 0, 0, 0, 1, 0, 99.39444, -92.97758, 0, 1);
  }

  30% {
    z-index: 99.09517;
    transform: matrix3d(0.59839, 0, 0, 0, 0, 0.59839, 0, 0, 0, 0, 1, 0, 114.96147, -90.48262, 0, 1);
  }

  31% {
    z-index: 99.12369;
    transform: matrix3d(0.6079, 0, 0, 0, 0, 0.6079, 0, 0, 0, 0, 1, 0, 130.07487, -87.63055, 0, 1);
  }

  32% {
    z-index: 99.15567;
    transform: matrix3d(0.61856, 0, 0, 0, 0, 0.61856, 0, 0, 0, 0, 1, 0, 144.67503, -84.43264, 0, 1);
  }

  33% {
    z-index: 99.19099;
    transform: matrix3d(0.63033, 0, 0, 0, 0, 0.63033, 0, 0, 0, 0, 1, 0, 158.70434, -80.9015, 0, 1);
  }

  34% {
    z-index: 99.22949;
    transform: matrix3d(0.64316, 0, 0, 0, 0, 0.64316, 0, 0, 0, 0, 1, 0, 172.10748, -77.05106, 0, 1);
  }

  35% {
    z-index: 99.27103;
    transform: matrix3d(0.65701, 0, 0, 0, 0, 0.65701, 0, 0, 0, 0, 1, 0, 184.83158, -72.89652, 0, 1);
  }

  36% {
    z-index: 99.31546;
    transform: matrix3d(0.67182, 0, 0, 0, 0, 0.67182, 0, 0, 0, 0, 1, 0, 196.82649, -68.45427, 0, 1);
  }

  37% {
    z-index: 99.36258;
    transform: matrix3d(0.68753, 0, 0, 0, 0, 0.68753, 0, 0, 0, 0, 1, 0, 208.04493, -63.74182, 0, 1);
  }

  38% {
    z-index: 99.41222;
    transform: matrix3d(0.70407, 0, 0, 0, 0, 0.70407, 0, 0, 0, 0, 1, 0, 218.4427, -58.77778, 0, 1);
  }

  39% {
    z-index: 99.46418;
    transform: matrix3d(0.72139, 0, 0, 0, 0, 0.72139, 0, 0, 0, 0, 1, 0, 227.97887, -53.58172, 0, 1);
  }

  40% {
    z-index: 99.51826;
    transform: matrix3d(0.73942, 0, 0, 0, 0, 0.73942, 0, 0, 0, 0, 1, 0, 236.61593, -48.17414, 0, 1);
  }

  41% {
    z-index: 99.57424;
    transform: matrix3d(0.75808, 0, 0, 0, 0, 0.75808, 0, 0, 0, 0, 1, 0, 244.31993, -42.57636, 0, 1);
  }

  42% {
    z-index: 99.6319;
    transform: matrix3d(0.7773, 0, 0, 0, 0, 0.7773, 0, 0, 0, 0, 1, 0, 251.06067, -36.81045, 0, 1);
  }

  43% {
    z-index: 99.69101;
    transform: matrix3d(0.797, 0, 0, 0, 0, 0.797, 0, 0, 0, 0, 1, 0, 256.81175, -30.89914, 0, 1);
  }

  44% {
    z-index: 99.75134;
    transform: matrix3d(0.81711, 0, 0, 0, 0, 0.81711, 0, 0, 0, 0, 1, 0, 261.55076, -24.86574, 0, 1);
  }

  45% {
    z-index: 99.81266;
    transform: matrix3d(0.83755, 0, 0, 0, 0, 0.83755, 0, 0, 0, 0, 1, 0, 265.25934, -18.73401, 0, 1);
  }

  46% {
    z-index: 99.87472;
    transform: matrix3d(0.85824, 0, 0, 0, 0, 0.85824, 0, 0, 0, 0, 1, 0, 267.92326, -12.52811, 0, 1);
  }

  47% {
    z-index: 99.93728;
    transform: matrix3d(0.87909, 0, 0, 0, 0, 0.87909, 0, 0, 0, 0, 1, 0, 269.5325, -6.27248, 0, 1);
  }

  48% {
    z-index: 100.00008;
    transform: matrix3d(0.90003, 0, 0, 0, 0, 0.90003, 0, 0, 0, 0, 1, 0, 270.08133, 0.00827, 0, 1);
  }

  49% {
    z-index: 100;
    transform: matrix3d(0.9, 0, 0, 0, 0, 0.9, 0, 0, 0, 0, 1, 0, 270, 0, 0, 1);
  }

  50% {
    z-index: 100.06279;
    transform: matrix3d(0.92093, 0, 0, 0, 0, 0.92093, 0, 0, 0, 0, 1, 0, 269.46722, 6.27905, 0, 1);
  }

  51% {
    z-index: 100.12533;
    transform: matrix3d(0.94178, 0, 0, 0, 0, 0.94178, 0, 0, 0, 0, 1, 0, 267.87097, 12.53332, 0, 1);
  }

  52% {
    z-index: 100.18738;
    transform: matrix3d(0.96246, 0, 0, 0, 0, 0.96246, 0, 0, 0, 0, 1, 0, 265.21756, 18.73813, 0, 1);
  }

  53% {
    z-index: 100.24869;
    transform: matrix3d(0.9829, 0, 0, 0, 0, 0.9829, 0, 0, 0, 0, 1, 0, 261.51745, 24.86899, 0, 1);
  }

  54% {
    z-index: 100.30902;
    transform: matrix3d(1.00301, 0, 0, 0, 0, 1.00301, 0, 0, 0, 0, 1, 0, 256.78526, 30.9017, 0, 1);
  }

  55% {
    z-index: 100.36812;
    transform: matrix3d(1.02271, 0, 0, 0, 0, 1.02271, 0, 0, 0, 0, 1, 0, 251.03965, 36.81246, 0, 1);
  }

  56% {
    z-index: 100.42578;
    transform: matrix3d(1.04193, 0, 0, 0, 0, 1.04193, 0, 0, 0, 0, 1, 0, 244.3033, 42.57793, 0, 1);
  }

  57% {
    z-index: 100.48175;
    transform: matrix3d(1.06058, 0, 0, 0, 0, 1.06058, 0, 0, 0, 0, 1, 0, 236.6028, 48.17537, 0, 1);
  }

  58% {
    z-index: 100.53583;
    transform: matrix3d(1.07861, 0, 0, 0, 0, 1.07861, 0, 0, 0, 0, 1, 0, 227.96854, 53.58268, 0, 1);
  }

  59% {
    z-index: 100.58779;
    transform: matrix3d(1.09593, 0, 0, 0, 0, 1.09593, 0, 0, 0, 0, 1, 0, 218.43459, 58.77853, 0, 1);
  }

  60% {
    z-index: 100.63742;
    transform: matrix3d(1.11247, 0, 0, 0, 0, 1.11247, 0, 0, 0, 0, 1, 0, 208.03858, 63.7424, 0, 1);
  }

  61% {
    z-index: 100.68455;
    transform: matrix3d(1.12818, 0, 0, 0, 0, 1.12818, 0, 0, 0, 0, 1, 0, 196.82153, 68.45471, 0, 1);
  }

  62% {
    z-index: 100.72897;
    transform: matrix3d(1.14299, 0, 0, 0, 0, 1.14299, 0, 0, 0, 0, 1, 0, 184.82772, 72.89686, 0, 1);
  }

  63% {
    z-index: 100.77051;
    transform: matrix3d(1.15684, 0, 0, 0, 0, 1.15684, 0, 0, 0, 0, 1, 0, 172.10448, 77.05132, 0, 1);
  }

  64% {
    z-index: 100.80902;
    transform: matrix3d(1.16967, 0, 0, 0, 0, 1.16967, 0, 0, 0, 0, 1, 0, 158.70202, 80.9017, 0, 1);
  }

  65% {
    z-index: 100.84433;
    transform: matrix3d(1.18144, 0, 0, 0, 0, 1.18144, 0, 0, 0, 0, 1, 0, 144.67323, 84.43279, 0, 1);
  }

  66% {
    z-index: 100.87631;
    transform: matrix3d(1.1921, 0, 0, 0, 0, 1.1921, 0, 0, 0, 0, 1, 0, 130.07349, 87.63067, 0, 1);
  }

  67% {
    z-index: 100.90483;
    transform: matrix3d(1.20161, 0, 0, 0, 0, 1.20161, 0, 0, 0, 0, 1, 0, 114.96041, 90.48271, 0, 1);
  }

  68% {
    z-index: 100.92978;
    transform: matrix3d(1.20993, 0, 0, 0, 0, 1.20993, 0, 0, 0, 0, 1, 0, 99.39363, 92.97765, 0, 1);
  }

  69% {
    z-index: 100.95106;
    transform: matrix3d(1.21702, 0, 0, 0, 0, 1.21702, 0, 0, 0, 0, 1, 0, 83.43459, 95.10565, 0, 1);
  }

  70% {
    z-index: 100.96858;
    transform: matrix3d(1.22286, 0, 0, 0, 0, 1.22286, 0, 0, 0, 0, 1, 0, 67.14627, 96.85832, 0, 1);
  }

  71% {
    z-index: 100.98229;
    transform: matrix3d(1.22743, 0, 0, 0, 0, 1.22743, 0, 0, 0, 0, 1, 0, 50.59295, 98.22873, 0, 1);
  }

  72% {
    z-index: 100.99211;
    transform: matrix3d(1.2307, 0, 0, 0, 0, 1.2307, 0, 0, 0, 0, 1, 0, 33.83997, 99.21147, 0, 1);
  }

  73% {
    z-index: 100.99803;
    transform: matrix3d(1.23268, 0, 0, 0, 0, 1.23268, 0, 0, 0, 0, 1, 0, 16.95344, 99.80267, 0, 1);
  }

  74% {
    z-index: 101;
    transform: matrix3d(1.23333, 0, 0, 0, 0, 1.23333, 0, 0, 0, 0, 1, 0, 0, 100, 0, 1);
  }

  75% {
    z-index: 100.99803;
    transform: matrix3d(1.23268, 0, 0, 0, 0, 1.23268, 0, 0, 0, 0, 1, 0, -16.95344, 99.80267, 0, 1);
  }

  76% {
    z-index: 100.99211;
    transform: matrix3d(1.2307, 0, 0, 0, 0, 1.2307, 0, 0, 0, 0, 1, 0, -33.83997, 99.21147, 0, 1);
  }

  77% {
    z-index: 100.98229;
    transform: matrix3d(1.22743, 0, 0, 0, 0, 1.22743, 0, 0, 0, 0, 1, 0, -50.59295, 98.22873, 0, 1);
  }

  78% {
    z-index: 100.96858;
    transform: matrix3d(1.22286, 0, 0, 0, 0, 1.22286, 0, 0, 0, 0, 1, 0, -67.14627, 96.85832, 0, 1);
  }

  79% {
    z-index: 100.95106;
    transform: matrix3d(1.21702, 0, 0, 0, 0, 1.21702, 0, 0, 0, 0, 1, 0, -83.43459, 95.10565, 0, 1);
  }

  80% {
    z-index: 100.92978;
    transform: matrix3d(1.20993, 0, 0, 0, 0, 1.20993, 0, 0, 0, 0, 1, 0, -99.39363, 92.97765, 0, 1);
  }

  81% {
    z-index: 100.90483;
    transform: matrix3d(1.20161, 0, 0, 0, 0, 1.20161, 0, 0, 0, 0, 1, 0, -114.96041, 90.48271, 0, 1);
  }

  82% {
    z-index: 100.87631;
    transform: matrix3d(1.1921, 0, 0, 0, 0, 1.1921, 0, 0, 0, 0, 1, 0, -130.07349, 87.63067, 0, 1);
  }

  83% {
    z-index: 100.84433;
    transform: matrix3d(1.18144, 0, 0, 0, 0, 1.18144, 0, 0, 0, 0, 1, 0, -144.67323, 84.43279, 0, 1);
  }

  84% {
    z-index: 100.80902;
    transform: matrix3d(1.16967, 0, 0, 0, 0, 1.16967, 0, 0, 0, 0, 1, 0, -158.70202, 80.9017, 0, 1);
  }

  85% {
    z-index: 100.77051;
    transform: matrix3d(1.15684, 0, 0, 0, 0, 1.15684, 0, 0, 0, 0, 1, 0, -172.10448, 77.05132, 0, 1);
  }

  86% {
    z-index: 100.72897;
    transform: matrix3d(1.14299, 0, 0, 0, 0, 1.14299, 0, 0, 0, 0, 1, 0, -184.82772, 72.89686, 0, 1);
  }

  87% {
    z-index: 100.68455;
    transform: matrix3d(1.12818, 0, 0, 0, 0, 1.12818, 0, 0, 0, 0, 1, 0, -196.82153, 68.45471, 0, 1);
  }

  88% {
    z-index: 100.63742;
    transform: matrix3d(1.11247, 0, 0, 0, 0, 1.11247, 0, 0, 0, 0, 1, 0, -208.03858, 63.7424, 0, 1);
  }

  89% {
    z-index: 100.58779;
    transform: matrix3d(1.09593, 0, 0, 0, 0, 1.09593, 0, 0, 0, 0, 1, 0, -218.43459, 58.77853, 0, 1);
  }

  90% {
    z-index: 100.53583;
    transform: matrix3d(1.07861, 0, 0, 0, 0, 1.07861, 0, 0, 0, 0, 1, 0, -227.96854, 53.58268, 0, 1);
  }

  91% {
    z-index: 100.48175;
    transform: matrix3d(1.06058, 0, 0, 0, 0, 1.06058, 0, 0, 0, 0, 1, 0, -236.6028, 48.17537, 0, 1);
  }

  92% {
    z-index: 100.42578;
    transform: matrix3d(1.04193, 0, 0, 0, 0, 1.04193, 0, 0, 0, 0, 1, 0, -244.3033, 42.57793, 0, 1);
  }

  93% {
    z-index: 100.36812;
    transform: matrix3d(1.02271, 0, 0, 0, 0, 1.02271, 0, 0, 0, 0, 1, 0, -251.03965, 36.81246, 0, 1);
  }

  94% {
    z-index: 100.30902;
    transform: matrix3d(1.00301, 0, 0, 0, 0, 1.00301, 0, 0, 0, 0, 1, 0, -256.78526, 30.9017, 0, 1);
  }

  95% {
    z-index: 100.24869;
    transform: matrix3d(0.9829, 0, 0, 0, 0, 0.9829, 0, 0, 0, 0, 1, 0, -261.51745, 24.86899, 0, 1);
  }

  96% {
    z-index: 100.18738;
    transform: matrix3d(0.96246, 0, 0, 0, 0, 0.96246, 0, 0, 0, 0, 1, 0, -265.21756, 18.73813, 0, 1);
  }

  97% {
    z-index: 100.12533;
    transform: matrix3d(0.94178, 0, 0, 0, 0, 0.94178, 0, 0, 0, 0, 1, 0, -267.87097, 12.53332, 0, 1);
  }

  98% {
    z-index: 100.06279;
    transform: matrix3d(0.92093, 0, 0, 0, 0, 0.92093, 0, 0, 0, 0, 1, 0, -269.46722, 6.27905, 0, 1);
  }

  99% {
    z-index: 100;
    transform: matrix3d(0.9, 0, 0, 0, 0, 0.9, 0, 0, 0, 0, 1, 0, -270, 0, 0, 1);
  }

  100% {
    z-index: 99.93721;
    transform: matrix3d(0.87907, 0, 0, 0, 0, 0.87907, 0, 0, 0, 0, 1, 0, -269.46722, -6.27905, 0, 1);
  }
}

@keyframes rotate8 {
  0% {
    z-index: 99.01771;
    transform: matrix3d(0.57257, 0, 0, 0, 0, 0.57257, 0, 0, 0, 0, 1, 0, 50.59331, -98.2287, 0, 1);
  }

  1% {
    z-index: 99.03142;
    transform: matrix3d(0.57714, 0, 0, 0, 0, 0.57714, 0, 0, 0, 0, 1, 0, 67.14674, -96.85828, 0, 1);
  }

  2% {
    z-index: 99.04894;
    transform: matrix3d(0.58298, 0, 0, 0, 0, 0.58298, 0, 0, 0, 0, 1, 0, 83.4352, -95.1056, 0, 1);
  }

  3% {
    z-index: 99.07022;
    transform: matrix3d(0.59007, 0, 0, 0, 0, 0.59007, 0, 0, 0, 0, 1, 0, 99.39444, -92.97758, 0, 1);
  }

  4% {
    z-index: 99.09517;
    transform: matrix3d(0.59839, 0, 0, 0, 0, 0.59839, 0, 0, 0, 0, 1, 0, 114.96147, -90.48262, 0, 1);
  }

  5% {
    z-index: 99.12369;
    transform: matrix3d(0.6079, 0, 0, 0, 0, 0.6079, 0, 0, 0, 0, 1, 0, 130.07487, -87.63055, 0, 1);
  }

  6% {
    z-index: 99.15567;
    transform: matrix3d(0.61856, 0, 0, 0, 0, 0.61856, 0, 0, 0, 0, 1, 0, 144.67503, -84.43264, 0, 1);
  }

  7% {
    z-index: 99.19099;
    transform: matrix3d(0.63033, 0, 0, 0, 0, 0.63033, 0, 0, 0, 0, 1, 0, 158.70434, -80.9015, 0, 1);
  }

  8% {
    z-index: 99.22949;
    transform: matrix3d(0.64316, 0, 0, 0, 0, 0.64316, 0, 0, 0, 0, 1, 0, 172.10748, -77.05106, 0, 1);
  }

  9% {
    z-index: 99.27103;
    transform: matrix3d(0.65701, 0, 0, 0, 0, 0.65701, 0, 0, 0, 0, 1, 0, 184.83158, -72.89652, 0, 1);
  }

  10% {
    z-index: 99.31546;
    transform: matrix3d(0.67182, 0, 0, 0, 0, 0.67182, 0, 0, 0, 0, 1, 0, 196.82649, -68.45427, 0, 1);
  }

  11% {
    z-index: 99.36258;
    transform: matrix3d(0.68753, 0, 0, 0, 0, 0.68753, 0, 0, 0, 0, 1, 0, 208.04493, -63.74182, 0, 1);
  }

  12% {
    z-index: 99.41222;
    transform: matrix3d(0.70407, 0, 0, 0, 0, 0.70407, 0, 0, 0, 0, 1, 0, 218.4427, -58.77778, 0, 1);
  }

  13% {
    z-index: 99.46418;
    transform: matrix3d(0.72139, 0, 0, 0, 0, 0.72139, 0, 0, 0, 0, 1, 0, 227.97887, -53.58172, 0, 1);
  }

  14% {
    z-index: 99.51826;
    transform: matrix3d(0.73942, 0, 0, 0, 0, 0.73942, 0, 0, 0, 0, 1, 0, 236.61593, -48.17414, 0, 1);
  }

  15% {
    z-index: 99.57424;
    transform: matrix3d(0.75808, 0, 0, 0, 0, 0.75808, 0, 0, 0, 0, 1, 0, 244.31993, -42.57636, 0, 1);
  }

  16% {
    z-index: 99.6319;
    transform: matrix3d(0.7773, 0, 0, 0, 0, 0.7773, 0, 0, 0, 0, 1, 0, 251.06067, -36.81045, 0, 1);
  }

  17% {
    z-index: 99.69101;
    transform: matrix3d(0.797, 0, 0, 0, 0, 0.797, 0, 0, 0, 0, 1, 0, 256.81175, -30.89914, 0, 1);
  }

  18% {
    z-index: 99.75134;
    transform: matrix3d(0.81711, 0, 0, 0, 0, 0.81711, 0, 0, 0, 0, 1, 0, 261.55076, -24.86574, 0, 1);
  }

  19% {
    z-index: 99.81266;
    transform: matrix3d(0.83755, 0, 0, 0, 0, 0.83755, 0, 0, 0, 0, 1, 0, 265.25934, -18.73401, 0, 1);
  }

  20% {
    z-index: 99.87472;
    transform: matrix3d(0.85824, 0, 0, 0, 0, 0.85824, 0, 0, 0, 0, 1, 0, 267.92326, -12.52811, 0, 1);
  }

  21% {
    z-index: 99.93728;
    transform: matrix3d(0.87909, 0, 0, 0, 0, 0.87909, 0, 0, 0, 0, 1, 0, 269.5325, -6.27248, 0, 1);
  }

  22% {
    z-index: 100.00008;
    transform: matrix3d(0.90003, 0, 0, 0, 0, 0.90003, 0, 0, 0, 0, 1, 0, 270.08133, 0.00827, 0, 1);
  }

  23% {
    z-index: 100;
    transform: matrix3d(0.9, 0, 0, 0, 0, 0.9, 0, 0, 0, 0, 1, 0, 270, 0, 0, 1);
  }

  24% {
    z-index: 100.06279;
    transform: matrix3d(0.92093, 0, 0, 0, 0, 0.92093, 0, 0, 0, 0, 1, 0, 269.46722, 6.27905, 0, 1);
  }

  25% {
    z-index: 100.12533;
    transform: matrix3d(0.94178, 0, 0, 0, 0, 0.94178, 0, 0, 0, 0, 1, 0, 267.87097, 12.53332, 0, 1);
  }

  26% {
    z-index: 100.18738;
    transform: matrix3d(0.96246, 0, 0, 0, 0, 0.96246, 0, 0, 0, 0, 1, 0, 265.21756, 18.73813, 0, 1);
  }

  27% {
    z-index: 100.24869;
    transform: matrix3d(0.9829, 0, 0, 0, 0, 0.9829, 0, 0, 0, 0, 1, 0, 261.51745, 24.86899, 0, 1);
  }

  28% {
    z-index: 100.30902;
    transform: matrix3d(1.00301, 0, 0, 0, 0, 1.00301, 0, 0, 0, 0, 1, 0, 256.78526, 30.9017, 0, 1);
  }

  29% {
    z-index: 100.36812;
    transform: matrix3d(1.02271, 0, 0, 0, 0, 1.02271, 0, 0, 0, 0, 1, 0, 251.03965, 36.81246, 0, 1);
  }

  30% {
    z-index: 100.42578;
    transform: matrix3d(1.04193, 0, 0, 0, 0, 1.04193, 0, 0, 0, 0, 1, 0, 244.3033, 42.57793, 0, 1);
  }

  31% {
    z-index: 100.48175;
    transform: matrix3d(1.06058, 0, 0, 0, 0, 1.06058, 0, 0, 0, 0, 1, 0, 236.6028, 48.17537, 0, 1);
  }

  32% {
    z-index: 100.53583;
    transform: matrix3d(1.07861, 0, 0, 0, 0, 1.07861, 0, 0, 0, 0, 1, 0, 227.96854, 53.58268, 0, 1);
  }

  33% {
    z-index: 100.58779;
    transform: matrix3d(1.09593, 0, 0, 0, 0, 1.09593, 0, 0, 0, 0, 1, 0, 218.43459, 58.77853, 0, 1);
  }

  34% {
    z-index: 100.63742;
    transform: matrix3d(1.11247, 0, 0, 0, 0, 1.11247, 0, 0, 0, 0, 1, 0, 208.03858, 63.7424, 0, 1);
  }

  35% {
    z-index: 100.68455;
    transform: matrix3d(1.12818, 0, 0, 0, 0, 1.12818, 0, 0, 0, 0, 1, 0, 196.82153, 68.45471, 0, 1);
  }

  36% {
    z-index: 100.72897;
    transform: matrix3d(1.14299, 0, 0, 0, 0, 1.14299, 0, 0, 0, 0, 1, 0, 184.82772, 72.89686, 0, 1);
  }

  37% {
    z-index: 100.77051;
    transform: matrix3d(1.15684, 0, 0, 0, 0, 1.15684, 0, 0, 0, 0, 1, 0, 172.10448, 77.05132, 0, 1);
  }

  38% {
    z-index: 100.80902;
    transform: matrix3d(1.16967, 0, 0, 0, 0, 1.16967, 0, 0, 0, 0, 1, 0, 158.70202, 80.9017, 0, 1);
  }

  39% {
    z-index: 100.84433;
    transform: matrix3d(1.18144, 0, 0, 0, 0, 1.18144, 0, 0, 0, 0, 1, 0, 144.67323, 84.43279, 0, 1);
  }

  40% {
    z-index: 100.87631;
    transform: matrix3d(1.1921, 0, 0, 0, 0, 1.1921, 0, 0, 0, 0, 1, 0, 130.07349, 87.63067, 0, 1);
  }

  41% {
    z-index: 100.90483;
    transform: matrix3d(1.20161, 0, 0, 0, 0, 1.20161, 0, 0, 0, 0, 1, 0, 114.96041, 90.48271, 0, 1);
  }

  42% {
    z-index: 100.92978;
    transform: matrix3d(1.20993, 0, 0, 0, 0, 1.20993, 0, 0, 0, 0, 1, 0, 99.39363, 92.97765, 0, 1);
  }

  43% {
    z-index: 100.95106;
    transform: matrix3d(1.21702, 0, 0, 0, 0, 1.21702, 0, 0, 0, 0, 1, 0, 83.43459, 95.10565, 0, 1);
  }

  44% {
    z-index: 100.96858;
    transform: matrix3d(1.22286, 0, 0, 0, 0, 1.22286, 0, 0, 0, 0, 1, 0, 67.14627, 96.85832, 0, 1);
  }

  45% {
    z-index: 100.98229;
    transform: matrix3d(1.22743, 0, 0, 0, 0, 1.22743, 0, 0, 0, 0, 1, 0, 50.59295, 98.22873, 0, 1);
  }

  46% {
    z-index: 100.99211;
    transform: matrix3d(1.2307, 0, 0, 0, 0, 1.2307, 0, 0, 0, 0, 1, 0, 33.83997, 99.21147, 0, 1);
  }

  47% {
    z-index: 100.99803;
    transform: matrix3d(1.23268, 0, 0, 0, 0, 1.23268, 0, 0, 0, 0, 1, 0, 16.95344, 99.80267, 0, 1);
  }

  48% {
    z-index: 101;
    transform: matrix3d(1.23333, 0, 0, 0, 0, 1.23333, 0, 0, 0, 0, 1, 0, 0, 100, 0, 1);
  }

  49% {
    z-index: 100.99803;
    transform: matrix3d(1.23268, 0, 0, 0, 0, 1.23268, 0, 0, 0, 0, 1, 0, -16.95344, 99.80267, 0, 1);
  }

  50% {
    z-index: 100.99211;
    transform: matrix3d(1.2307, 0, 0, 0, 0, 1.2307, 0, 0, 0, 0, 1, 0, -33.83997, 99.21147, 0, 1);
  }

  51% {
    z-index: 100.98229;
    transform: matrix3d(1.22743, 0, 0, 0, 0, 1.22743, 0, 0, 0, 0, 1, 0, -50.59295, 98.22873, 0, 1);
  }

  52% {
    z-index: 100.96858;
    transform: matrix3d(1.22286, 0, 0, 0, 0, 1.22286, 0, 0, 0, 0, 1, 0, -67.14627, 96.85832, 0, 1);
  }

  53% {
    z-index: 100.95106;
    transform: matrix3d(1.21702, 0, 0, 0, 0, 1.21702, 0, 0, 0, 0, 1, 0, -83.43459, 95.10565, 0, 1);
  }

  54% {
    z-index: 100.92978;
    transform: matrix3d(1.20993, 0, 0, 0, 0, 1.20993, 0, 0, 0, 0, 1, 0, -99.39363, 92.97765, 0, 1);
  }

  55% {
    z-index: 100.90483;
    transform: matrix3d(1.20161, 0, 0, 0, 0, 1.20161, 0, 0, 0, 0, 1, 0, -114.96041, 90.48271, 0, 1);
  }

  56% {
    z-index: 100.87631;
    transform: matrix3d(1.1921, 0, 0, 0, 0, 1.1921, 0, 0, 0, 0, 1, 0, -130.07349, 87.63067, 0, 1);
  }

  57% {
    z-index: 100.84433;
    transform: matrix3d(1.18144, 0, 0, 0, 0, 1.18144, 0, 0, 0, 0, 1, 0, -144.67323, 84.43279, 0, 1);
  }

  58% {
    z-index: 100.80902;
    transform: matrix3d(1.16967, 0, 0, 0, 0, 1.16967, 0, 0, 0, 0, 1, 0, -158.70202, 80.9017, 0, 1);
  }

  59% {
    z-index: 100.77051;
    transform: matrix3d(1.15684, 0, 0, 0, 0, 1.15684, 0, 0, 0, 0, 1, 0, -172.10448, 77.05132, 0, 1);
  }

  60% {
    z-index: 100.72897;
    transform: matrix3d(1.14299, 0, 0, 0, 0, 1.14299, 0, 0, 0, 0, 1, 0, -184.82772, 72.89686, 0, 1);
  }

  61% {
    z-index: 100.68455;
    transform: matrix3d(1.12818, 0, 0, 0, 0, 1.12818, 0, 0, 0, 0, 1, 0, -196.82153, 68.45471, 0, 1);
  }

  62% {
    z-index: 100.63742;
    transform: matrix3d(1.11247, 0, 0, 0, 0, 1.11247, 0, 0, 0, 0, 1, 0, -208.03858, 63.7424, 0, 1);
  }

  63% {
    z-index: 100.58779;
    transform: matrix3d(1.09593, 0, 0, 0, 0, 1.09593, 0, 0, 0, 0, 1, 0, -218.43459, 58.77853, 0, 1);
  }

  64% {
    z-index: 100.53583;
    transform: matrix3d(1.07861, 0, 0, 0, 0, 1.07861, 0, 0, 0, 0, 1, 0, -227.96854, 53.58268, 0, 1);
  }

  65% {
    z-index: 100.48175;
    transform: matrix3d(1.06058, 0, 0, 0, 0, 1.06058, 0, 0, 0, 0, 1, 0, -236.6028, 48.17537, 0, 1);
  }

  66% {
    z-index: 100.42578;
    transform: matrix3d(1.04193, 0, 0, 0, 0, 1.04193, 0, 0, 0, 0, 1, 0, -244.3033, 42.57793, 0, 1);
  }

  67% {
    z-index: 100.36812;
    transform: matrix3d(1.02271, 0, 0, 0, 0, 1.02271, 0, 0, 0, 0, 1, 0, -251.03965, 36.81246, 0, 1);
  }

  68% {
    z-index: 100.30902;
    transform: matrix3d(1.00301, 0, 0, 0, 0, 1.00301, 0, 0, 0, 0, 1, 0, -256.78526, 30.9017, 0, 1);
  }

  69% {
    z-index: 100.24869;
    transform: matrix3d(0.9829, 0, 0, 0, 0, 0.9829, 0, 0, 0, 0, 1, 0, -261.51745, 24.86899, 0, 1);
  }

  70% {
    z-index: 100.18738;
    transform: matrix3d(0.96246, 0, 0, 0, 0, 0.96246, 0, 0, 0, 0, 1, 0, -265.21756, 18.73813, 0, 1);
  }

  71% {
    z-index: 100.12533;
    transform: matrix3d(0.94178, 0, 0, 0, 0, 0.94178, 0, 0, 0, 0, 1, 0, -267.87097, 12.53332, 0, 1);
  }

  72% {
    z-index: 100.06279;
    transform: matrix3d(0.92093, 0, 0, 0, 0, 0.92093, 0, 0, 0, 0, 1, 0, -269.46722, 6.27905, 0, 1);
  }

  73% {
    z-index: 100;
    transform: matrix3d(0.9, 0, 0, 0, 0, 0.9, 0, 0, 0, 0, 1, 0, -270, 0, 0, 1);
  }

  74% {
    z-index: 99.93721;
    transform: matrix3d(0.87907, 0, 0, 0, 0, 0.87907, 0, 0, 0, 0, 1, 0, -269.46722, -6.27905, 0, 1);
  }

  75% {
    z-index: 99.87467;
    transform: matrix3d(
      0.85822,
      0,
      0,
      0,
      0,
      0.85822,
      0,
      0,
      0,
      0,
      1,
      0,
      -267.87097,
      -12.53332,
      0,
      1
    );
  }

  76% {
    z-index: 99.81262;
    transform: matrix3d(
      0.83754,
      0,
      0,
      0,
      0,
      0.83754,
      0,
      0,
      0,
      0,
      1,
      0,
      -265.21756,
      -18.73813,
      0,
      1
    );
  }

  77% {
    z-index: 99.75131;
    transform: matrix3d(0.8171, 0, 0, 0, 0, 0.8171, 0, 0, 0, 0, 1, 0, -261.51745, -24.86899, 0, 1);
  }

  78% {
    z-index: 99.69098;
    transform: matrix3d(0.79699, 0, 0, 0, 0, 0.79699, 0, 0, 0, 0, 1, 0, -256.78526, -30.9017, 0, 1);
  }

  79% {
    z-index: 99.63188;
    transform: matrix3d(
      0.77729,
      0,
      0,
      0,
      0,
      0.77729,
      0,
      0,
      0,
      0,
      1,
      0,
      -251.03965,
      -36.81246,
      0,
      1
    );
  }

  80% {
    z-index: 99.57422;
    transform: matrix3d(0.75807, 0, 0, 0, 0, 0.75807, 0, 0, 0, 0, 1, 0, -244.3033, -42.57793, 0, 1);
  }

  81% {
    z-index: 99.51825;
    transform: matrix3d(0.73942, 0, 0, 0, 0, 0.73942, 0, 0, 0, 0, 1, 0, -236.6028, -48.17537, 0, 1);
  }

  82% {
    z-index: 99.46417;
    transform: matrix3d(
      0.72139,
      0,
      0,
      0,
      0,
      0.72139,
      0,
      0,
      0,
      0,
      1,
      0,
      -227.96854,
      -53.58268,
      0,
      1
    );
  }

  83% {
    z-index: 99.41221;
    transform: matrix3d(
      0.70407,
      0,
      0,
      0,
      0,
      0.70407,
      0,
      0,
      0,
      0,
      1,
      0,
      -218.43459,
      -58.77853,
      0,
      1
    );
  }

  84% {
    z-index: 99.36258;
    transform: matrix3d(0.68753, 0, 0, 0, 0, 0.68753, 0, 0, 0, 0, 1, 0, -208.03857, -63.7424, 0, 1);
  }

  85% {
    z-index: 99.31545;
    transform: matrix3d(
      0.67182,
      0,
      0,
      0,
      0,
      0.67182,
      0,
      0,
      0,
      0,
      1,
      0,
      -196.82153,
      -68.45471,
      0,
      1
    );
  }

  86% {
    z-index: 99.27103;
    transform: matrix3d(
      0.65701,
      0,
      0,
      0,
      0,
      0.65701,
      0,
      0,
      0,
      0,
      1,
      0,
      -184.82772,
      -72.89686,
      0,
      1
    );
  }

  87% {
    z-index: 99.22949;
    transform: matrix3d(
      0.64316,
      0,
      0,
      0,
      0,
      0.64316,
      0,
      0,
      0,
      0,
      1,
      0,
      -172.10447,
      -77.05132,
      0,
      1
    );
  }

  88% {
    z-index: 99.19098;
    transform: matrix3d(0.63033, 0, 0, 0, 0, 0.63033, 0, 0, 0, 0, 1, 0, -158.70201, -80.9017, 0, 1);
  }

  89% {
    z-index: 99.15567;
    transform: matrix3d(
      0.61856,
      0,
      0,
      0,
      0,
      0.61856,
      0,
      0,
      0,
      0,
      1,
      0,
      -144.67323,
      -84.43279,
      0,
      1
    );
  }

  90% {
    z-index: 99.12369;
    transform: matrix3d(0.6079, 0, 0, 0, 0, 0.6079, 0, 0, 0, 0, 1, 0, -130.07348, -87.63067, 0, 1);
  }

  91% {
    z-index: 99.09517;
    transform: matrix3d(0.59839, 0, 0, 0, 0, 0.59839, 0, 0, 0, 0, 1, 0, -114.96039, -90.4827, 0, 1);
  }

  92% {
    z-index: 99.07022;
    transform: matrix3d(0.59007, 0, 0, 0, 0, 0.59007, 0, 0, 0, 0, 1, 0, -99.39361, -92.97765, 0, 1);
  }

  93% {
    z-index: 99.04894;
    transform: matrix3d(0.58298, 0, 0, 0, 0, 0.58298, 0, 0, 0, 0, 1, 0, -83.43456, -95.10565, 0, 1);
  }

  94% {
    z-index: 99.03142;
    transform: matrix3d(0.57714, 0, 0, 0, 0, 0.57714, 0, 0, 0, 0, 1, 0, -67.14622, -96.85831, 0, 1);
  }

  95% {
    z-index: 99.01771;
    transform: matrix3d(0.57257, 0, 0, 0, 0, 0.57257, 0, 0, 0, 0, 1, 0, -50.59289, -98.22872, 0, 1);
  }

  96% {
    z-index: 99.00789;
    transform: matrix3d(0.5693, 0, 0, 0, 0, 0.5693, 0, 0, 0, 0, 1, 0, -33.83989, -99.21146, 0, 1);
  }

  97% {
    z-index: 99.00197;
    transform: matrix3d(0.56732, 0, 0, 0, 0, 0.56732, 0, 0, 0, 0, 1, 0, -16.95333, -99.80266, 0, 1);
  }

  98% {
    z-index: 99;
    transform: matrix3d(0.56667, 0, 0, 0, 0, 0.56667, 0, 0, 0, 0, 1, 0, 0.00015, -99.99999, 0, 1);
  }

  99% {
    z-index: 99.00197;
    transform: matrix3d(0.56732, 0, 0, 0, 0, 0.56732, 0, 0, 0, 0, 1, 0, 16.95364, -99.80266, 0, 1);
  }

  100% {
    z-index: 99.00789;
    transform: matrix3d(0.5693, 0, 0, 0, 0, 0.5693, 0, 0, 0, 0, 1, 0, 33.84024, -99.21145, 0, 1);
  }
}
</style>
