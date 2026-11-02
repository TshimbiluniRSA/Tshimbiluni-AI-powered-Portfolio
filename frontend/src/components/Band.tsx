import falls from '../assets/photos/witpoortjie-falls.jpg';
import './Band.css';

/** The page's one rest: a full-width picture from Roodepoort. */
export default function Band() {
  return (
    <figure className="band">
      <div className="band__frame" data-reveal>
        <img
          src={falls}
          alt="Witpoortjie Falls dropping over red quartzite cliffs into green bush"
          width={1944}
          height={1296}
          loading="lazy"
          decoding="async"
        />
      </div>
      <figcaption className="small muted">
        Witpoortjie Falls, Walter Sisulu National Botanical Garden, Roodepoort
      </figcaption>
    </figure>
  );
}
