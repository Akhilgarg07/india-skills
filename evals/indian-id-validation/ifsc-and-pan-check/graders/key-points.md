---
type: llm
---

PASS only if the response does ALL of the following:
1. Says the IFSC RBISONDPA01 is invalid because the 5th character must be the digit zero (0), and it is the letter O. It may suggest RBIS0NDPA01 as the likely intended value.
2. Says the PAN ABCXE1234F is invalid because its 4th character (X) is not a valid holder-status code (valid codes include P, C, H, F, A, B, T, G, J, L).
3. Notes that format checks alone cannot prove that the IFSC branch or the PAN actually exists.

FAIL if either value is called valid.
