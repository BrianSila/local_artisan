import { useState } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowRight,
  Search,
  MapPin,
  Handshake,
  MessageCircle,
  CalendarCheck,
  ShieldCheck,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api, metadata, type Location } from "@/lib/local/api";
import { CategoryIcon, ErrorNotice, Loading, useCategories } from "./shared";
import workshop from "@/assets/artisan-workshop.jpg";
export function HomePage() {
  const [term, setTerm] = useState("");
  const [county, setCounty] = useState("");
  const navigate = useNavigate();
  const categories = useCategories();
  const counties = useQuery({
    queryKey: ["counties"],
    queryFn: () => api<Location[]>("/locations/counties"),
    retry: false,
  });
  return (
    <main>
      <section className="hero">
        <img
          className="hero-image"
          src={workshop}
          alt="A carpenter carefully shaping a wooden table in his workshop"
          width={1920}
          height={1024}
        />
        <div className="container hero-content">
          <div className="eyebrow">
            <span className="eyebrow-dot" /> GREAT WORK STARTS CLOSE TO HOME
          </div>
          <h1>
            Local Artisan.
            <br />
            Skilled hands.
            <br />
            <span>Closer to home.</span>
          </h1>
          <p className="hero-description">
            From the everyday fixes to the big ideas, find local artisans who bring your plans to
            life.
          </p>
          <form
            className="hero-search"
            onSubmit={(e) => {
              e.preventDefault();
              navigate({ to: "/browse", search: { search_term: term, county_id: county } });
            }}
          >
            <div className="search-keyword">
              <Search size={19} />
              <input
                aria-label="What service do you need?"
                placeholder="What service do you need?"
                value={term}
                onChange={(e) => setTerm(e.target.value)}
              />
            </div>
            <div className="search-location">
              <MapPin size={17} />
              <select
                aria-label="Select county"
                value={county}
                onChange={(e) => setCounty(e.target.value)}
              >
                <option value="">Anywhere</option>
                {counties.data?.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
            <Button type="submit">
              Find a service <ArrowRight />
            </Button>
          </form>
          <div className="popular-searches">
            <span>A little inspiration:</span>
            <Link to="/browse" search={{ search_term: "Plumbing" }}>
              Plumbing
            </Link>
            <Link to="/browse" search={{ search_term: "Carpentry" }}>
              Carpentry
            </Link>
            <Link to="/browse" search={{ search_term: "Electrical" }}>
              Electrical
            </Link>
            <Link to="/browse" search={{ search_term: "Tailoring" }}>
              Tailoring
            </Link>
          </div>
        </div>
        <div className="craft-label">
          <strong>Built with skill. Made with care.</strong>
          <span>Celebrating the hands behind the work.</span>
        </div>
      </section>
      <div className="trust-strip">
        <div className="container trust-inner">
          {[
            { Icon: MapPin, title: "Local, not far away", text: "Find services in your community" },
            {
              Icon: Handshake,
              title: "Skills for everyday life",
              text: "Small fixes to bigger projects",
            },
            {
              Icon: CalendarCheck,
              title: "Book on your terms",
              text: "Request a time that works for you",
            },
            {
              Icon: MessageCircle,
              title: "Real conversations",
              text: "Connect directly on WhatsApp",
            },
          ].map(({ Icon, title, text }) => (
            <div className="trust-item" key={title}>
              <Icon />
              <div>
                <strong>{title}</strong>
                <span>{text}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      <section className="section container">
        <div className="section-heading">
          <div>
            <h2>What can we help you with?</h2>
            <p>Explore local skills for your home, business, and everything in between.</p>
          </div>
          <Link className="text-link" to="/browse">
            Explore all services <ArrowRight size={15} />
          </Link>
        </div>
        {categories.isLoading ? (
          <Loading />
        ) : categories.error ? (
          <ErrorNotice error={categories.error} retry={() => categories.refetch()} />
        ) : categories.data?.length ? (
          <div className="categories-grid">
            {categories.data.map((c) => (
              <Link
                className="category-tile"
                to="/browse"
                search={{ category_slug: c.slug }}
                key={c.id}
              >
                <span className="category-icon">
                  <CategoryIcon name={c.icon_name} />
                </span>
                {c.name}
              </Link>
            ))}
          </div>
        ) : (
          <p className="page-subtitle">
            Service categories will appear here as they become available.
          </p>
        )}
      </section>
      <section className="section how-section">
        <div className="container">
          <div className="how-heading">
            <div className="section-label">A GOOD CONNECTION, SIMPLY MADE</div>
            <h2>Your next project starts here.</h2>
            <p>Less searching around. More getting things done.</p>
          </div>
          <div className="steps">
            <div>
              <span className="step-number">01</span>
              <h3>Find the right skill</h3>
              <p>
                Explore services and narrow your search to your county, your neighbourhood, or
                somewhere nearby.
              </p>
            </div>
            <div>
              <span className="step-number">02</span>
              <h3>Make a connection</h3>
              <p>
                Look through the service details, discuss your needs, and request a booking that
                fits your schedule.
              </p>
            </div>
            <div>
              <span className="step-number">03</span>
              <h3>Bring your project to life</h3>
              <p>
                Work with a local artisan and follow your booking from the first request to the
                finished job.
              </p>
            </div>
          </div>
        </div>
      </section>
      <section className="section container">
        <div className="section-heading">
          <div>
            <div className="section-label">ROOTED IN OUR COMMUNITIES</div>
            <h2>Good work deserves to be found.</h2>
            <p>Behind every skill is a person, a story, and a livelihood.</p>
          </div>
          <Link className="text-link" to="/about">
            Meet Local Artisan <ArrowRight size={15} />
          </Link>
        </div>
        <div className="community-band">
          <div>
            <h2>
              Your craft. Your community.
              <br />
              Your next opportunity.
            </h2>
            <p>Make your skills visible. Connect with people looking for what you do.</p>
          </div>
          <Button asChild size="lg">
            <Link to="/auth" search={{ mode: "register", role: "artisan" }}>
              Join as an artisan <ArrowRight />
            </Link>
          </Button>
        </div>
      </section>
    </main>
  );
}
export function AboutPage() {
  return (
    <main className="container page-main">
      <div className="about-intro">
        <div className="section-label">OUR STORY</div>
        <h1>
          Local Artisan.
          <br />
          Good work, closer to home.
        </h1>
        <p>
          Kenya is full of skilled hands. Local Artisan exists to help people find them — connecting
          everyday needs with the craftspeople and service providers in our communities.
        </p>
      </div>
      <img
        className="about-photo"
        src={workshop}
        alt="A local carpenter working with care in a sunlit workshop"
        width={1920}
        height={1024}
        loading="lazy"
      />
      <div className="about-values">
        <div>
          <h2>Rooted in community</h2>
          <p>
            We believe local skills should be easy to discover. A search in your county can be the
            start of a meaningful working relationship.
          </p>
        </div>
        <div>
          <h2>Respect for the craft</h2>
          <p>
            Every service represents time, experience, and care. We give artisans a place to present
            their work and build their own opportunities.
          </p>
        </div>
        <div>
          <h2>Clear connections</h2>
          <p>
            Explore services, request a booking, and talk directly about the work you need. We put
            practical connections first.
          </p>
        </div>
      </div>
      <div className="form-actions">
        <Button asChild>
          <Link to="/browse">
            Find your next service <ArrowRight />
          </Link>
        </Button>
        <Button variant="outline" asChild>
          <Link to="/auth" search={{ mode: "register", role: "artisan" }}>
            Share your skills
          </Link>
        </Button>
      </div>
    </main>
  );
}
