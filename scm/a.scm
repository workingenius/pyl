(define (gcd a b)
  (if (> b a) (gcd b a)
    (let ((r (remainder a b)))
      (if (= 0 r)
	b
	(gcd b r)))))

(display (gcd 8 16))
