export interface News {
  id: number;
  title: string;
  description: string;
  date: string;
  image?: {
    url: string;
    name?: string;
    alternativeText?: string;
  };
}
