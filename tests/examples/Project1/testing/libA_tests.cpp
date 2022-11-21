#include "./catch.hpp"

#include <libA.hpp>

TEST_CASE("libA Unit Tests.")
{
  libA::print();
  CHECK(true);
}
