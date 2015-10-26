![jar_of_marbles](http://www.jlao.net/wp-content/uploads/2015/10/jar_of_marbles.jpg) 我们有时候会有进行数据抽样的需要，比如要从文件中随机取出若干行，或从数据集中随机取出若干数据进行分析。通常情况下这并不是什么难事，比如 Python 中直接提供了 `random.sample()` 来做这件事，Numpy 中更提供了功能更为强大的 `numpy.random.choice()`。然而这些东西都有一个问题，就是你必须把整个数据集读到内存里。如果数据集超出了内存的限制，或者要对一个持续的输入流做抽样，即**从包含 $n$ 个项目的集合中（等概率）选取 $k$ 个样本，其中 $n$ 为很大或未知**，又该怎么做呢？ 

#### 蓄水池

这里介绍的方法都有一个共同的特点，就是建立一个“蓄水池” (reservoir)，池的大小就是要选出的样本大小，如果元素没有充满池子，那自然每个元素都被选进来了。如果池子满了以后还有新的元素来了，就以一定概率从池中换一个元素出去。 举个具体的例子来说吧，输入的是自然数流 1, 2, 3, 4, 5, ... 样本数 $k = 3$，也就是说要保证等概率地从流中选出 3 个元素。前三个数自然先把位子都站好了，这时候 $P = 1$。 输入第四个数 4 的时候，我们先要保证它进入池中的概率是 $\frac{3}{4}$。然后换掉谁呢？1 ~ 3 这三个数被换掉的概率都应该是 $\frac{1}{4}$，于是 1 ~ 4 这四个数留在池中的概率都是 $\frac{3}{4}$。 具体怎么做呢？一种做法是对第 $n$ 项，生成一个 $1 \sim n$ 的随机数 $j$。如果 $j \leq k$，则用第 $n$ 项替换第 $j$ 项。 这个方法对不对呢？利用数学归纳法，假设 $n = N$ 时，第 $i$ 项被抽到的概率 $$P_i(N) = \frac{k}{N}$$ 则 $n = N+1$ 时，第 $N+1$ 项被选中的概率 $$P_{N+1}(N+1) = \frac{k}{N+1}$$ 而第 $1 \sim N$ 项则要再去掉它在前 $k$ 个元素中被新加进来的项替换掉的情况 $$ \begin{align} P_i(N+1) & = \frac{k}{N} \cdot \left(1 - P_{N+1} \cdot \frac{1}{k}\right)\\ &= \frac{k}{N} \cdot \left(1 - \frac{1}{N+1}\right) \\ &= \frac{k}{N+1} \end{align} $$ 我们已经知道，对于 $n = k$ 时，第 $i$ 项被抽到的概率都是 $P_i(k) = 1 = \frac{k}{n}$。于是得证。 这就是所谓的“Algorithm R”。这个东西实现起来也很简单：

<pre class="lang:python decode:true ">import random
import sys

def reservoirSample(stream, sample_size):
    result = []
    for index, line in enumerate(stream):
        if index < sample_size:
            result.append(line)
        else:
            r = int(random.random() * (index + 1))
            if r < sample_size:
                result[r] = line
    return result

if __name__ == '__main__':
    print(reservoirSample(sys.stdin, 10))</pre>

#### 换个思路

上面这个方法是不是很巧妙？太巧妙了。不过我们还可以有另外一个更简单的思路。比如说，对进来的每一项，都给它指派一个 $[0,1]$ 均匀分布的随机数。然后把所有数字按照升序或者降序排列。最后选出最前面（或者最后面）的 $k$ 项就可以了。 这个东西看起来非常直观啊。不过证明起来……有点搞。不想看的同学请直接跳过：

> 假设一共有 $n$ 项，我们已经定好了要选出的最大的 $k$ 项，那么对于第 $k+1$ 大的那一项，有 $n-k$ 个均匀分布的变量 $u_i$ 都比它小，所以它的分布函数是 $$F(x) = \prod_{i=1}^{n-k}\mathbb{P}(u_i \leq x) = x^{n-k}$$ 而剩下的 $k$ 个变量都比 $x$ 大的概率则是 $(1-x)^k$。于是，要选出一组特定的 $k$ 个元素的样本 $s$ 的概率是 @_@ $$P = \int_0^1 (1-x)^k \mathrm{d} F(x) = (n-k)\int_0^1(1-x)^k x^{n-k-1} \mathrm{d} x$$ 注意到右边是个欧拉积分…… Beta 函数在整数参量的时候有 $$\mathrm{B}(x,y) = \int_0 ^1 t^x(1-t)^y \mathrm{d} t = \frac{x!\,y!}{(x+y+1)!}$$ 套进去就得到了 $$P = (n-k)\,\mathrm{B}(k, n-k-1) = \frac{k!\, (n-k)!}{n!}=\binom{n}{k} ^{-1}$$ 正好是从 $n$ 个样本中选 $k$ 个元素时选到特定一组的概率。证毕。

实现起来倒是很方便，只需要维护一个大小为 $k$ 的堆就可以了：

<pre class="lang:python decode:true ">import random
import sys
import heapq

def reservoirSample(stream, sample_size):
    result = []
    for index, line in enumerate(stream):
        key = random.random()
        if index < sample_size:
            heapq.heappush(result, (key, line))
        elif key > heapq.nsmallest(1, result)[0][0]:
            heapq.heappushpop(result, (key, line))
    return list(zip(*result))[1]

if __name__ == '__main__':
    print(reservoirSample(sys.stdin, 10))</pre>

这个方法也很好，只不过是每次操作要维护这个堆需要 $O(\log k)$ 的时间，稍微慢了那么一点点。但是这个思路还有其他的优势，我们后面再谈。 好了，今天先说到这吧。但是问题还没有完。这两种方法需要产生多少随机数呢？$n -k$ 个。而且每一个元素都要放进来比较。有没有快一点的方法呢？且听[下回分解](http://www.jlao.net/zh/technology/10268/)。
