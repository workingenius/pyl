; 用一个重递归算法，测试提出 analyze 环节的加速效果

(define (fib n)
 (cond
  ((< n 1) 'error)
  ((= n 1) 1)
  ((= n 2) 1)
  (else (+ (fib (- n 1)) (fib (- n 2))))))

(display (fib 22))
