# NIVEX PPT JS 引擎

每个 PPT 的 `<script>` 部分使用以下标准代码。直接复制，不需要修改。

## 导航 + 进度条 + 动画重置

```javascript
const slides = document.querySelectorAll('.slide');
const progress = document.getElementById('progress');
const currentSlideEl = document.getElementById('currentSlide');
const totalSlidesEl = document.getElementById('totalSlides');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

let currentSlide = 0;
const totalSlides = slides.length;

totalSlidesEl.textContent = totalSlides;

function updateSlide(index) {
  slides.forEach((slide, i) => {
    slide.classList.remove('active');
    slide.querySelectorAll('.animate-in, .animate-left, .animate-right, .animate-scale').forEach(el => {
      el.style.opacity = '0';
    });
  });

  slides[index].classList.add('active');
  currentSlideEl.textContent = index + 1;
  progress.style.width = ((index + 1) / totalSlides * 100) + '%';
}

function nextSlide() {
  currentSlide = (currentSlide + 1) % totalSlides;
  updateSlide(currentSlide);
}

function prevSlide() {
  currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
  updateSlide(currentSlide);
}

// 键盘导航：← → 空格 回车
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'Enter') {
    e.preventDefault();
    nextSlide();
  } else if (e.key === 'ArrowLeft') {
    e.preventDefault();
    prevSlide();
  }
});

// 按钮导航
nextBtn.addEventListener('click', nextSlide);
prevBtn.addEventListener('click', prevSlide);

// 触摸滑动（移动端）
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', (e) => {
  touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', (e) => {
  touchEndX = e.changedTouches[0].screenX;
  if (touchStartX - touchEndX > 50) {
    nextSlide();
  } else if (touchEndX - touchStartX > 50) {
    prevSlide();
  }
});

// 点击翻页（避开导航按钮）
document.querySelector('.slides-container').addEventListener('click', (e) => {
  if (!e.target.closest('.nav-btn')) {
    nextSlide();
  }
});

// 初始化
updateSlide(0);
```

## 导航按钮 HTML

放在 `</div><!-- slides-container -->` 之后：

```html
<!-- Navigation -->
<div class="nav">
  <button class="nav-btn" id="prevBtn">←</button>
  <button class="nav-btn" id="nextBtn">→</button>
</div>

<div class="slide-counter">
  <span id="currentSlide">1</span> / <span id="totalSlides">{总页数}</span>
</div>
```

## 进度条 HTML

放在 `<body>` 开头：

```html
<div class="progress" id="progress"></div>
```

## 交互方式汇总

| 方式 | 前进 | 后退 |
|------|------|------|
| 键盘 | → / 空格 / 回车 | ← |
| 鼠标 | 点击页面任意位置 | 点击 ← 按钮 |
| 触摸 | 左滑 | 右滑 |
| 按钮 | → 按钮 | ← 按钮 |
